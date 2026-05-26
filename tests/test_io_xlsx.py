import pandas as pd
from conftest import FIXTURE_PATH
import io_xlsx


def test_load_returns_long_form_dataframe():
    df = io_xlsx.load_cross_q_check(FIXTURE_PATH)
    expected_cols = {"order_num", "coder", "question", "answer", "notes"}
    assert set(df.columns) == expected_cols


def test_load_one_row_per_participating_coder_per_question():
    df = io_xlsx.load_cross_q_check(FIXTURE_PATH)
    # 10 orders * up to 4 coders * 6 questions = up to 240 rows
    # but only the 2 coders per order are present; Bridget never appears.
    # Each row has 2 coders * 6 questions = 12 entries -> 10 * 12 = 120
    assert len(df) == 120
    assert set(df["coder"].unique()) == {"Leah", "Rachel", "Alia"}


def test_load_normalizes_blank_to_none():
    df = io_xlsx.load_cross_q_check(FIXTURE_PATH)
    # Order 1, Leah, Q4 — should be None (blank in fixture)
    row = df[(df["order_num"] == 1) & (df["coder"] == "Leah") & (df["question"] == "Q4")]
    assert len(row) == 1
    assert row["answer"].iloc[0] is None


def test_load_preserves_yes_no_answers():
    df = io_xlsx.load_cross_q_check(FIXTURE_PATH)
    row = df[(df["order_num"] == 3) & (df["coder"] == "Leah") & (df["question"] == "Q1")]
    assert row["answer"].iloc[0] == "yes"


def test_load_preserves_multi_label_string():
    df = io_xlsx.load_cross_q_check(FIXTURE_PATH)
    row = df[(df["order_num"] == 6) & (df["coder"] == "Leah") & (df["question"] == "Q4")]
    assert row["answer"].iloc[0] == "academia, the public"
