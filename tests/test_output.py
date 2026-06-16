import json
import pytest
from nrcli.output import (
    extract_fields,
    flatten_dict,
    to_json,
    to_csv,
    format_output,
    write_output,
)


class TestExtractFields:
    def test_extracts_specified_fields(self):
        data = {"id": "123", "name": "test", "status": "active", "extra": "ignored"}

        result = extract_fields(data, ["id", "name"])

        assert result == {"id": "123", "name": "test"}

    def test_missing_fields_return_none(self):
        data = {"id": "123"}

        result = extract_fields(data, ["id", "missing"])

        assert result == {"id": "123", "missing": None}

    def test_empty_fields_returns_empty_dict(self):
        data = {"id": "123"}

        result = extract_fields(data, [])

        assert result == {}


class TestFlattenDict:
    def test_flattens_nested_dict(self):
        data = {"outer": {"inner": "value"}}

        result = flatten_dict(data)

        assert result == {"outer.inner": "value"}

    def test_deeply_nested(self):
        data = {"a": {"b": {"c": "deep"}}}

        result = flatten_dict(data)

        assert result == {"a.b.c": "deep"}

    def test_lists_become_json(self):
        data = {"items": [1, 2, 3]}

        result = flatten_dict(data)

        assert result == {"items": "[1, 2, 3]"}

    def test_mixed_content(self):
        data = {
            "id": "123",
            "meta": {"version": "1.0", "tags": ["a", "b"]},
        }

        result = flatten_dict(data)

        assert result["id"] == "123"
        assert result["meta.version"] == "1.0"
        assert result["meta.tags"] == '["a", "b"]'


class TestToJson:
    def test_formats_with_indent(self):
        data = {"key": "value"}

        result = to_json(data)

        assert result == '{\n  "key": "value"\n}'

    def test_handles_nested_structures(self):
        data = {"outer": {"inner": [1, 2]}}

        result = to_json(data)
        parsed = json.loads(result)

        assert parsed == data


class TestToCsv:
    def test_single_row(self):
        data = [{"id": "1", "name": "test"}]

        result = to_csv(data)

        lines = result.strip().replace("\r\n", "\n").split("\n")
        assert lines[0] == "id,name"
        assert lines[1] == "1,test"

    def test_multiple_rows(self):
        data = [
            {"id": "1", "name": "first"},
            {"id": "2", "name": "second"},
        ]

        result = to_csv(data)

        lines = result.strip().split("\n")
        assert len(lines) == 3

    def test_with_field_filter(self):
        data = [{"id": "1", "name": "test", "extra": "ignored"}]

        result = to_csv(data, fields=["id"])

        lines = result.strip().replace("\r\n", "\n").split("\n")
        assert lines[0] == "id"
        assert lines[1] == "1"

    def test_empty_data_returns_empty_string(self):
        result = to_csv([])

        assert result == ""

    def test_flattens_nested_dicts(self):
        data = [{"id": "1", "meta": {"version": "1.0"}}]

        result = to_csv(data)

        assert "meta.version" in result
        assert "1.0" in result


class TestFormatOutput:
    def test_dict_as_json(self):
        data = {"id": "123"}

        result = format_output(data)

        assert json.loads(result) == data

    def test_dict_as_csv(self):
        data = {"id": "123", "name": "test"}

        result = format_output(data, csv_format=True)

        assert "id" in result
        assert "123" in result

    def test_list_as_json(self):
        data = [{"id": "1"}, {"id": "2"}]

        result = format_output(data)

        assert json.loads(result) == data

    def test_list_as_csv(self):
        data = [{"id": "1"}, {"id": "2"}]

        result = format_output(data, csv_format=True)

        lines = result.strip().split("\n")
        assert len(lines) == 3

    def test_field_filtering_dict(self):
        data = {"id": "123", "name": "test", "extra": "ignored"}

        result = format_output(data, fields="id,name")
        parsed = json.loads(result)

        assert "extra" not in parsed
        assert parsed["id"] == "123"

    def test_field_filtering_list(self):
        data = [{"id": "1", "extra": "x"}, {"id": "2", "extra": "y"}]

        result = format_output(data, fields="id")
        parsed = json.loads(result)

        assert all("extra" not in item for item in parsed)


class TestWriteOutput:
    def test_writes_to_file(self, tmp_path):
        data = {"id": "123"}
        output_file = tmp_path / "output.json"

        write_output(data, str(output_file))

        content = output_file.read_text()
        assert json.loads(content) == data

    def test_writes_csv_to_file(self, tmp_path):
        data = {"id": "123", "name": "test"}
        output_file = tmp_path / "output.csv"

        write_output(data, str(output_file), csv_format=True)

        content = output_file.read_text()
        assert "id" in content
        assert "123" in content

    def test_prints_to_stdout_when_no_file(self, capsys):
        data = {"id": "123"}

        write_output(data)

        captured = capsys.readouterr()
        assert json.loads(captured.out.strip()) == data
