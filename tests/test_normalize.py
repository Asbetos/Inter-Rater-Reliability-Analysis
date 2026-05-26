import normalize


def test_normalize_yes_no():
    assert normalize.normalize_categorical("yes") == "yes"
    assert normalize.normalize_categorical("YES ") == "yes"
    assert normalize.normalize_categorical(" No") == "no"
    assert normalize.normalize_categorical("(blank)") is None
    assert normalize.normalize_categorical(None) is None
    assert normalize.normalize_categorical("") is None


def test_split_label_set_single_label():
    assert normalize.split_label_set("the public") == frozenset({"the public"})


def test_split_label_set_two_labels():
    assert normalize.split_label_set("academia, the public") == frozenset(
        {"academia", "the public"}
    )


def test_split_label_set_with_quoted_compound_separator():
    # Q5 has labels like '"In coordination with"/"in consultation with"'
    # which contain commas inside quotes. Our split is naive — we treat the
    # whole thing as one label. Test this invariant.
    s = '"In coordination with"/"in consultation with"'
    assert normalize.split_label_set(s) == frozenset({s.lower()})


def test_split_label_set_handles_other_token():
    # The "other (add next col)" token contains parentheses but no comma;
    # the comma split should leave it intact.
    s = "experts, other (add next col)"
    assert normalize.split_label_set(s) == frozenset({"experts", "other (add next col)"})


def test_split_label_set_blank():
    assert normalize.split_label_set(None) == frozenset()
    assert normalize.split_label_set("") == frozenset()
    assert normalize.split_label_set("(blank)") == frozenset()


def test_jaccard_pair_identical():
    a = frozenset({"a", "b"}); b = frozenset({"a", "b"})
    assert normalize.jaccard(a, b) == 1.0


def test_jaccard_pair_partial():
    a = frozenset({"academia", "the public"})
    b = frozenset({"the public"})
    assert normalize.jaccard(a, b) == 0.5


def test_jaccard_pair_disjoint():
    a = frozenset({"academia"}); b = frozenset({"tribes"})
    assert normalize.jaccard(a, b) == 0.0


def test_jaccard_both_empty_returns_nan():
    # Conventional choice: both empty = undefined (skip in mean)
    import math
    assert math.isnan(normalize.jaccard(frozenset(), frozenset()))
