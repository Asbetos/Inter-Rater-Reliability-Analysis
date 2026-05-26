"""Build the IRR test fixture workbook.

Run from irr_analysis/:
    /home/G39248410/citizen_voice/venv/bin/python tests/build_fixture.py

Produces tests/fixtures/mini_cross_check.xlsx with the schema of the real
cross_q_check workbook, 10 rows, 3 coders (Leah, Rachel, Alia), Bridget absent.
"""
from pathlib import Path
import openpyxl

CODERS = ["Leah", "Bridget", "Rachel", "Alia"]
QUESTIONS = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
HEADER = (
    ["order.num", "num.coders"]
    + [f"q{i}.agree" for i in range(1, 7)]
    + [f"q1.rest.{c}" for c in CODERS]
    + CODERS
    + [
        col
        for c in CODERS
        for col in [
            f"Q1.{c}", f"Q1.notes.{c}",
            f"Q2.{c}", f"Q2.notes.{c}",
            f"Q3.{c}", f"Q3.notes.{c}",
            f"Q4.{c}", f"Q4.notes.{c}",
            f"Q5.{c}", f"Q5.notes.{c}",
            f"Q6.{c}", f"notes.{c}",
        ]
    ]
)

# (q1, q2, q3, q4, q5, q6) tuples per coder; None means coder didn't code that row.
# Layout: row_no -> { coder_name: (Q1, Q2, Q3, Q4, Q5, Q6) or None }
ROWS = {
    1:  {"Leah": ("no",  None, None, None, None, "no"),
         "Rachel": ("no", None, None, None, None, "no")},
    2:  {"Leah": ("no",  None, None, None, None, "no"),
         "Rachel": ("no", None, None, None, None, "no")},
    3:  {"Leah": ("yes", "no", "no", "the public",
                  "Create or extend comment periods", "no"),
         "Rachel": ("yes", "no", "no", "the public",
                    "Create or extend comment periods", "no")},
    4:  {"Leah": ("yes", "no", "no", "the public",
                  "Advisory board or committee", "no"),
         "Rachel": ("no",  None, None, None, None, "no")},
    5:  {"Leah": ("no",  None, None, None, None, "no"),
         "Alia": ("no",  None, None, None, None, "yes")},
    6:  {"Leah": ("yes", "no", "no", "academia, the public",
                  "Advisory board or committee", "yes"),
         "Alia": ("yes", "no", "no", "the public",
                  "Advisory board or committee", "yes")},
    7:  {"Rachel": ("no", None, None, None, None, "no"),
         "Alia":   ("no", None, None, None, None, "no")},
    8:  {"Rachel": ("yes", "no", "no", "experts",
                    "Create or extend comment periods", "no"),
         "Alia":   ("yes", "no", "no", "experts",
                    "other (not listed)", "no")},
    9:  {"Leah":   ("no", None, None, None, None, "no"),
         "Rachel": ("no", None, None, None, None, "no")},
    10: {"Leah": ("yes", "no", "no", "tribes",
                  "Advisory board or committee", "no"),
         "Alia": ("yes", "no", "no", "tribes",
                  "Advisory board or committee", "no")},
}


def cell_for(row_data, coder, qkey):
    """Return cell value for the per-coder per-question column."""
    if coder not in row_data:
        return None
    answers = row_data[coder]
    idx = {"Q1": 0, "Q2": 1, "Q3": 2, "Q4": 3, "Q5": 4, "Q6": 5}[qkey]
    return answers[idx]


def build():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(HEADER)
    for order in sorted(ROWS):
        row_data = ROWS[order]
        n_coders = len(row_data)
        row = [order, n_coders]
        # qN.agree booleans (sanity column; we recompute in code anyway)
        for q in QUESTIONS:
            vals = [cell_for(row_data, c, q) for c in CODERS if c in row_data]
            if all(v is None for v in vals):
                row.append(True)  # both blank == "agree" in source schema
            else:
                row.append(len(set(vals)) <= 1)
        # q1.rest.<coder> — "ok" if coder participated, blank otherwise
        for c in CODERS:
            row.append("ok" if c in row_data else None)
        # Coder indicator columns: "1" if coder participated, blank otherwise
        for c in CODERS:
            row.append("1" if c in row_data else None)
        # Per-coder per-question answers + notes
        for c in CODERS:
            for q in QUESTIONS:
                row.append(cell_for(row_data, c, q))
                row.append(None)  # notes column always blank in fixture
        # Strip last notes.<coder> placeholder — schema only has notes.<coder>
        # at the end of each coder block, not Q6.notes.<coder>. We already
        # appended "None" for Q6 notes; that's actually the "notes.<coder>" col.
        ws.append(row)
    out = Path(__file__).parent / "fixtures" / "mini_cross_check.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    build()
