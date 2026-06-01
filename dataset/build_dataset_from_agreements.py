"""IRR dataset builder v2 -- agreement-sheet boolean methodology.

Reads ONLY the qN.agree boolean columns from each volume's chosen
agreement sheet. Attributes each disagreement to the coder pair assigned
to that order.num (per the Assignment sheet).

Pipeline:
    1. List Drive workbooks; filter to the 20-volume whitelist
    2. For each volume: pick the agreement sheet (hardcoded override OR
       earliest-by-name fallback via pick_agreement_sheet.pick())
    3. Read qN.agree booleans (agreement_booleans.read)
    4. Read coder->order_set mapping (assignment_sheet.parse)
    5. Aggregate disagreements per (coder, question) and per (pair, question)
    6. Compute number_coded_prior across volumes
    7. Write CSV + Parquet to outputs/

Outputs:
    outputs/irr_dataset_v2_per_coder.csv (+ .parquet)
    outputs/irr_dataset_v2_per_pair.csv  (+ .parquet)
    outputs/irr_dataset_v2_metadata.csv
    outputs/irr_dataset_v2_errors.csv (only if any volume errored)
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent))

import pandas as pd

import agreement_booleans
import assignment_sheet
import auth
import drive_source
import drive_walk
import number_coded
import parse_agreement_sheet
import pick_agreement_sheet
import volume_whitelist


QUESTIONS = ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7")


def _find_sheet(wb, target_name: str) -> Optional[str]:
    """Match `target_name` against wb.sheetnames, case- and whitespace-tolerant.

    Falls back to digits-match within agreement sheets if exact name not found.
    """
    target_norm = re.sub(r"\s+", " ", target_name.strip().lower())
    for sn in wb.sheetnames:
        if re.sub(r"\s+", " ", sn.strip().lower()) == target_norm:
            return sn
    digits = re.search(r"\d+", target_name)
    if digits:
        d = digits.group(0)
        for sn in wb.sheetnames:
            if "agreement" in sn.lower() and d in sn:
                return sn
    return None


def _is_legacy_volume(canonical_label: str) -> bool:
    m = re.search(r"[Vv]olume\s*(\d+)", canonical_label)
    if not m:
        return False
    return int(m.group(1)) <= 63


def _resolve_chosen_date(sheet_name: str, drive_mtime) -> date:
    """Best-effort date resolution from the chosen sheet name + Drive mtime."""
    cands = parse_agreement_sheet.candidate_dates(sheet_name)
    if not cands:
        return drive_mtime.date()
    valid = [
        date(drive_mtime.year, m, d)
        for (m, d) in cands
        if date(drive_mtime.year, m, d) <= drive_mtime.date()
    ]
    if not valid:
        valid = [date(drive_mtime.year - 1, cands[0][0], cands[0][1])]
    return min(valid)


def process_volume(
    src: drive_source.DriveSource,
    handle: drive_source.WorkbookHandle,
    canonical_label: str,
) -> Dict:
    """Process one volume; return its per-coder, per-pair, metadata."""
    wb = src.open(handle)
    mtime = src.last_modified(handle)

    # Pick the agreement sheet
    override = volume_whitelist.override_sheet_for(handle.name)
    if override:
        chosen_sheet = _find_sheet(wb, override)
        if chosen_sheet is None:
            raise RuntimeError(
                f"override sheet {override!r} not found in {handle.name!r}; "
                f"available: {wb.sheetnames}"
            )
    else:
        agreement_sheets = [s for s in wb.sheetnames if "agreement" in s.lower()]
        pick_result = pick_agreement_sheet.pick(
            sheet_names=agreement_sheets,
            drive_mtime=mtime,
            overrides={},
            volume_id="",
        )
        chosen_sheet = pick_result["chosen_sheet"]
        if chosen_sheet is None:
            raise RuntimeError(
                f"could not pick agreement sheet for {handle.name!r}; "
                f"reason: {pick_result['manual_review_reason']}"
            )

    chosen_date = _resolve_chosen_date(chosen_sheet, mtime)

    # Read booleans + assignments
    agreement_data = agreement_booleans.read(wb, chosen_sheet)
    assignments = assignment_sheet.parse(wb)
    coders_present = sorted(assignments.keys())

    per_coder_rows: List[Dict] = []
    per_pair_rows: List[Dict] = []

    for q in QUESTIONS:
        # Skip questions not in this agreement sheet
        if not any(q in row for row in agreement_data.values()):
            continue

        # Per-coder aggregation
        for coder in coders_present:
            assigned_orders = assignments[coder]
            # Restrict to orders that actually appear in the agreement sheet
            relevant_orders = assigned_orders & set(agreement_data.keys())
            n_assigned = len(relevant_orders)
            if n_assigned == 0:
                continue
            n_dis = sum(
                1 for order in relevant_orders
                if agreement_data[order].get(q) is False
            )
            per_coder_rows.append({
                "coder": coder,
                "volume": canonical_label,
                "question": q,
                "n_assigned_orders": n_assigned,
                "n_disagreements": n_dis,
                "pct_agreement": (n_assigned - n_dis) / n_assigned,
            })

        # Per-pair aggregation
        for a, b in combinations(coders_present, 2):
            overlap = assignments[a] & assignments[b] & set(agreement_data.keys())
            n_overlap = len(overlap)
            if n_overlap == 0:
                continue
            n_dis = sum(
                1 for order in overlap
                if agreement_data[order].get(q) is False
            )
            per_pair_rows.append({
                "coder_a": a,
                "coder_b": b,
                "volume": canonical_label,
                "question": q,
                "n_overlap_orders": n_overlap,
                "n_disagreements": n_dis,
                "pct_agreement": (n_overlap - n_dis) / n_overlap,
            })

    return {
        "metadata": {
            "volume": canonical_label,
            "volume_file": handle.name,
            "chosen_sheet": chosen_sheet,
            "chosen_date": chosen_date.isoformat(),
            "drive_mtime": mtime.isoformat(),
            "n_orders_in_agreement_sheet": len(agreement_data),
            "coders_in_assignment": ", ".join(coders_present),
        },
        "per_coder_rows": per_coder_rows,
        "per_pair_rows": per_pair_rows,
        "participations": [
            (canonical_label, c, chosen_date) for c in coders_present
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--drive-folder-id", required=True)
    parser.add_argument("--credentials", required=True, type=Path)
    parser.add_argument("--token", type=Path, default=auth.DEFAULT_TOKEN_PATH)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    from googleapiclient.discovery import build
    creds = auth.get_credentials(args.credentials, args.token)
    service = build("drive", "v3", credentials=creds)
    src = drive_source.OAuthDriveSource(
        folder_id=args.drive_folder_id, service=service,
    )

    handles = drive_walk.list_eligible(src)
    # Annotate each handle with its canonical label, skip non-whitelisted
    whitelisted = []
    for h in handles:
        label = volume_whitelist.match_volume(h.name)
        if label:
            whitelisted.append((h, label))
    if not whitelisted:
        raise SystemExit(
            "No volumes matched the whitelist. Check whitelist constants."
        )
    print(f"matched {len(whitelisted)} whitelisted volumes")

    per_coder_all: List[Dict] = []
    per_pair_all: List[Dict] = []
    metadata_all: List[Dict] = []
    participations_all: List = []
    errors: List[Dict] = []

    for h, label in whitelisted:
        try:
            r = process_volume(src, h, label)
        except Exception as e:
            errors.append({"volume_file": h.name, "error": str(e)})
            print(f"ERROR processing {h.name}: {e}")
            continue
        per_coder_all.extend(r["per_coder_rows"])
        per_pair_all.extend(r["per_pair_rows"])
        metadata_all.append(r["metadata"])
        participations_all.extend(r["participations"])
        print(f"processed {label}: {len(r['per_coder_rows'])} coder rows, {len(r['per_pair_rows'])} pair rows")

    # number_coded_prior across volumes; dedupe (volume, coder)
    seen = set()
    unique_participations = []
    for p in participations_all:
        key = (p[0], p[1])
        if key in seen:
            continue
        seen.add(key)
        unique_participations.append(p)
    nc = number_coded.compute(unique_participations)

    # Enrich rows
    vol_meta = {m["volume"]: m for m in metadata_all}
    for r in per_coder_all:
        r["number_coded_prior"] = nc.get((r["volume"], r["coder"]), 0)
        r["is_legacy_volume"] = _is_legacy_volume(r["volume"])
        meta = vol_meta.get(r["volume"], {})
        r["agreement_sheet_date"] = meta.get("chosen_date", "")
        r["chosen_sheet"] = meta.get("chosen_sheet", "")
    for r in per_pair_all:
        r["number_coded_prior_a"] = nc.get((r["volume"], r["coder_a"]), 0)
        r["number_coded_prior_b"] = nc.get((r["volume"], r["coder_b"]), 0)
        r["is_legacy_volume"] = _is_legacy_volume(r["volume"])
        meta = vol_meta.get(r["volume"], {})
        r["agreement_sheet_date"] = meta.get("chosen_date", "")
        r["chosen_sheet"] = meta.get("chosen_sheet", "")

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    per_coder_df = pd.DataFrame(per_coder_all)
    per_pair_df = pd.DataFrame(per_pair_all)
    metadata_df = pd.DataFrame(metadata_all)
    per_coder_df.to_csv(out_dir / "irr_dataset_v2_per_coder.csv", index=False)
    if not per_coder_df.empty:
        per_coder_df.to_parquet(out_dir / "irr_dataset_v2_per_coder.parquet")
    per_pair_df.to_csv(out_dir / "irr_dataset_v2_per_pair.csv", index=False)
    if not per_pair_df.empty:
        per_pair_df.to_parquet(out_dir / "irr_dataset_v2_per_pair.parquet")
    metadata_df.to_csv(out_dir / "irr_dataset_v2_metadata.csv", index=False)
    if errors:
        pd.DataFrame(errors).to_csv(
            out_dir / "irr_dataset_v2_errors.csv", index=False,
        )
    print(
        f"v2 dataset: {len(per_coder_all)} per-coder rows, "
        f"{len(per_pair_all)} per-pair rows, "
        f"{len(metadata_all)} volumes processed, "
        f"{len(errors)} errored."
    )


if __name__ == "__main__":
    main()
