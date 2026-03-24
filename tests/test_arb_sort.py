import json
import pytest
from weblate_arb_sort._sort import sort_arb_content


def sorted_keys(content: str) -> list[str]:
    return list(json.loads(content).keys())


def test_regular_keys_sorted_alphabetically():
    data = {"zebra": "z", "apple": "a", "mango": "m"}
    result = sorted_keys(sort_arb_content(json.dumps(data)))
    assert result == ["apple", "mango", "zebra"]


def test_metadata_follows_parent_key():
    data = {
        "zebra": "z",
        "@zebra": {"description": "animal"},
        "apple": "a",
        "@apple": {"description": "fruit"},
    }
    result = sorted_keys(sort_arb_content(json.dumps(data)))
    assert result == ["apple", "@apple", "zebra", "@zebra"]


def test_locale_keys_at_top():
    data = {
        "hello": "Hello",
        "@@locale": "en",
        "@hello": {"description": "greeting"},
    }
    result = sorted_keys(sort_arb_content(json.dumps(data)))
    assert result[0] == "@@locale"
    assert result.index("hello") < result.index("@hello")


def test_orphaned_metadata_appended_at_end():
    data = {
        "apple": "a",
        "@orphan": {"description": "no parent"},
    }
    result = sorted_keys(sort_arb_content(json.dumps(data)))
    assert result[-1] == "@orphan"
    assert "apple" in result


def test_case_insensitive_sort():
    data = {"Banana": "B", "apple": "a", "Cherry": "C"}
    result = sorted_keys(sort_arb_content(json.dumps(data)))
    assert result == ["apple", "Banana", "Cherry"]


def test_invalid_json_raises():
    with pytest.raises(json.JSONDecodeError):
        sort_arb_content("not json")


def test_output_ends_with_newline():
    data = {"a": "1"}
    result = sort_arb_content(json.dumps(data))
    assert result.endswith("\n")


def test_multiple_locale_keys_kept_at_top_in_original_order():
    data = {"hello": "Hello", "@@locale": "en", "@@last_modified": "2024-01-01", "zebra": "z"}
    result = sorted_keys(sort_arb_content(json.dumps(data)))
    assert result[0] == "@@locale"
    assert result[1] == "@@last_modified"
    assert result.index("@@last_modified") < result.index("hello")
    assert result.index("@@last_modified") < result.index("zebra")


def test_empty_dict():
    result = sort_arb_content(json.dumps({}))
    assert json.loads(result) == {}


def test_only_locale_keys():
    data = {"@@locale": "en", "@@last_modified": "2024-01-01"}
    result = sorted_keys(sort_arb_content(json.dumps(data)))
    assert result == ["@@locale", "@@last_modified"]
