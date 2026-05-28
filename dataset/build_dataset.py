"""IRR dataset build orchestrator.

Subcommands:
    check-completeness  -- walk Drive, run completeness check, emit completeness_report.csv
    pick-sheets         -- for completed volumes, pick agreement sheet; emit manual_review.csv
    compute             -- full pipeline: walk -> completeness -> pick -> IRR -> join -> CSVs

Source selection: --local-root <path>  OR  --drive-folder-id <id> + --credentials <json>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

# Make sibling modules importable both as `python -m dataset.build_dataset`
# and as a direct script. The sibling modules use bare imports (e.g.
# `import drive_source`), so the dataset/ dir must be on sys.path AND
# the parent dir (so pilot modules like irr_metrics / normalize import too).
_HERE = Path(__file__).resolve().parent
_PKG_PARENT = _HERE.parent
for _p in (str(_HERE), str(_PKG_PARENT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import yaml

import auth
import completeness
import drive_source
import drive_walk
import irr_per_volume
import number_coded
import pick_agreement_sheet
import tracking_oracle


def _volume_id_from_filename(name: str) -> str:
    """Strip the .xlsx extension and normalize for use as a volume key."""
    return Path(name).stem


def _open_source(args):
    if args.local_root:
        return drive_source.LocalDriveSource(args.local_root)
    if not (args.drive_folder_id and args.credentials):
        raise SystemExit(
            "either --local-root OR --drive-folder-id + --credentials required"
        )
    from googleapiclient.discovery import build
    creds = auth.get_credentials(Path(args.credentials), Path(args.token))
    service = build("drive", "v3", credentials=creds)
    return drive_source.OAuthDriveSource(
        folder_id=args.drive_folder_id, service=service
    )


def _load_overrides(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text())
    return raw or {}


def _is_legacy_volume(vol_id: str) -> bool:
    """Volume number <= 63 is the legacy identifier-format cohort."""
    # Extract first integer token from the volume id (best-effort)
    digits = ""
    for ch in vol_id:
        if ch.isdigit():
            digits += ch
        elif digits:
            break
    if not digits:
        return False
    try:
        return int(digits) <= 63
    except ValueError:
        return False


def cmd_check_completeness(args):
    src = _open_source(args)
    tracker = tracking_oracle.load(src) if not args.local_root else {}
    handles = drive_walk.list_eligible(src)
    rows = []
    for h in handles:
        wb = src.open(h)
        result = completeness.check(wb, threshold=args.completeness_threshold)
        vol_id = _volume_id_from_filename(h.name)
        tracker_entry = tracker.get(vol_id, {})
        passes = result["passes"] or tracker_entry.get("complete", False)
        rows.append({
            "volume_file": h.name,
            "volume_id": vol_id,
            "passes": passes,
            "passes_heuristic": result["passes"],
            "passes_tracker": tracker_entry.get("complete", None),
            "heuristic_reason": result["reason"],
            "tracker_raw_status": tracker_entry.get("raw_status_text", ""),
            "n_agreement_sheets": len(result["agreement_sheets"]),
            **{
                f"fill_{c}": v
                for c, v in result["coder_fill_fractions"].items()
            },
        })
    out = Path(args.output_dir) / "completeness_report.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {out}")


def cmd_pick_sheets(args):
    src = _open_source(args)
    overrides = _load_overrides(Path(args.overrides))
    handles = drive_walk.list_eligible(src)
    manual_review = []
    picks = []
    for h in handles:
        wb = src.open(h)
        cresult = completeness.check(wb, threshold=args.completeness_threshold)
        if not cresult["passes"]:
            continue
        mtime = src.last_modified(h)
        vol_id = _volume_id_from_filename(h.name)
        result = pick_agreement_sheet.pick(
            sheet_names=cresult["agreement_sheets"],
            drive_mtime=mtime,
            overrides=overrides,
            volume_id=vol_id,
        )
        picks.append({
            "volume_id": vol_id,
            "volume_file": h.name,
            "chosen_sheet": result["chosen_sheet"],
            "chosen_date": result["chosen_date"].isoformat() if result["chosen_date"] else "",
        })
        if result["manual_review"]:
            manual_review.append({
                "volume_id": vol_id,
                "volume_file": h.name,
                "candidate_sheets": ";".join(cresult["agreement_sheets"]),
                "reason": result["manual_review_reason"],
            })

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(picks).to_csv(out_dir / "agreement_sheet_picks.csv", index=False)
    pd.DataFrame(manual_review).to_csv(out_dir / "manual_review.csv", index=False)
    print(f"wrote {out_dir/'agreement_sheet_picks.csv'}")
    print(f"wrote {out_dir/'manual_review.csv'} ({len(manual_review)} entries)")
    return picks


def cmd_compute(args):
    src = _open_source(args)
    overrides = _load_overrides(Path(args.overrides))
    handles = drive_walk.list_eligible(src)
    tracker = tracking_oracle.load(src) if not args.local_root else {}

    per_coder_all: List[Dict] = []
    per_pair_all: List[Dict] = []
    participations: List[number_coded.Participation] = []
    metadata_rows = []

    for h in handles:
        wb = src.open(h)
        cresult = completeness.check(wb, threshold=args.completeness_threshold)
        vol_id = _volume_id_from_filename(h.name)
        tracker_entry = tracker.get(vol_id, {})
        if not (cresult["passes"] or tracker_entry.get("complete", False)):
            continue

        mtime = src.last_modified(h)
        sheet_pick = pick_agreement_sheet.pick(
            sheet_names=cresult["agreement_sheets"],
            drive_mtime=mtime,
            overrides=overrides,
            volume_id=vol_id,
        )
        if sheet_pick["chosen_sheet"] is None:
            continue

        per_coder_rows, per_pair_rows = irr_per_volume.compute(wb)
        is_legacy = _is_legacy_volume(vol_id)
        sheet_date_iso = sheet_pick["chosen_date"].isoformat()

        for r in per_coder_rows:
            r["volume"] = vol_id
            r["agreement_sheet_date"] = sheet_date_iso
            r["is_legacy_volume"] = is_legacy
            per_coder_all.append(r)
            participations.append((vol_id, r["coder"], sheet_pick["chosen_date"]))
        for r in per_pair_rows:
            r["volume"] = vol_id
            r["agreement_sheet_date"] = sheet_date_iso
            r["is_legacy_volume"] = is_legacy
            per_pair_all.append(r)

        metadata_rows.append({
            "volume": vol_id,
            "volume_file": h.name,
            "chosen_sheet": sheet_pick["chosen_sheet"],
            "agreement_sheet_date": sheet_date_iso,
            "drive_mtime": mtime.isoformat(),
            "is_legacy_volume": is_legacy,
        })

    # Deduplicate participations (a coder appears once per volume)
    seen = set()
    unique_participations = []
    for p in participations:
        key = (p[0], p[1])
        if key in seen:
            continue
        seen.add(key)
        unique_participations.append(p)

    nc = number_coded.compute(unique_participations)
    for r in per_coder_all:
        r["number_coded_prior"] = nc.get((r["volume"], r["coder"]), 0)
    for r in per_pair_all:
        r["number_coded_prior_a"] = nc.get((r["volume"], r["coder_a"]), 0)
        r["number_coded_prior_b"] = nc.get((r["volume"], r["coder_b"]), 0)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    per_coder_df = pd.DataFrame(per_coder_all)
    per_pair_df = pd.DataFrame(per_pair_all)
    metadata_df = pd.DataFrame(metadata_rows)
    per_coder_df.to_csv(out_dir / "irr_dataset_per_coder.csv", index=False)
    if not per_coder_df.empty:
        per_coder_df.to_parquet(out_dir / "irr_dataset_per_coder.parquet")
    per_pair_df.to_csv(out_dir / "irr_dataset_per_pair.csv", index=False)
    if not per_pair_df.empty:
        per_pair_df.to_parquet(out_dir / "irr_dataset_per_pair.parquet")
    metadata_df.to_csv(out_dir / "dataset_metadata.csv", index=False)
    print(
        f"wrote {len(per_coder_all)} per-coder rows, "
        f"{len(per_pair_all)} per-pair rows to {out_dir}"
    )


def _add_common_args(parser):
    parser.add_argument(
        "--local-root", type=Path,
        help="path to local Drive mirror (skip OAuth)",
    )
    parser.add_argument("--drive-folder-id", help="Google Drive folder ID")
    parser.add_argument(
        "--credentials", type=Path, help="OAuth credentials.json",
    )
    parser.add_argument("--token", type=Path, default=auth.DEFAULT_TOKEN_PATH)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument(
        "--overrides", type=Path,
        default=Path(__file__).parent / "agreement_sheet_overrides.yaml",
    )
    parser.add_argument("--completeness-threshold", type=float, default=0.80)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for cmd, fn in [
        ("check-completeness", cmd_check_completeness),
        ("pick-sheets", cmd_pick_sheets),
        ("compute", cmd_compute),
    ]:
        sp = sub.add_parser(cmd)
        _add_common_args(sp)
        sp.set_defaults(func=fn)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
