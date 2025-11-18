import json

from src.converter import DialogConverter


def test_structured_log_spans_for_examples(tmp_path):
    converter = DialogConverter()
    text = '"Nada…" dijo.\n"Me contó un pajarito, sí, me dijo"\n"Vestite..." y se fue'
    converted, logger = converter.convert(text)

    # Save structured log to temp
    out = tmp_path / "out.json"
    logger.save_structured_log(out)
    data = json.loads(out.read_text(encoding="utf-8"))

    # We expect three entries
    assert len(data) == 3

    # Entry 1: "Nada…" dijo.
    e1 = data[0]
    assert e1["original"].startswith('"Nada')
    assert e1["original_fragment"] is not None
    assert e1["original_span"] is not None
    # The substring at span should equal the fragment
    span1 = e1["original_span"]
    start, end = span1
    assert e1["original"][start:end] == e1["original_fragment"]

    # Entry 2: Me contó...
    e2 = data[1]
    assert e2["original_fragment"] is not None
    span2 = e2["original_span"]
    start2, end2 = span2
    assert e2["original"][start2:end2] == e2["original_fragment"]

    # Entry 3: Vestite...
    e3 = data[2]
    assert e3["original_fragment"] is not None
    span3 = e3["original_span"]
    start3, end3 = span3
    assert e3["original"][start3:end3] == e3["original_fragment"]
