import json
import pytest
from unittest.mock import patch, MagicMock


class TestSearchCommand:
    def test_outputs_search_results(self, mock_client, capsys):
        mock_gql = MagicMock()

        mock_node = MagicMock()
        mock_node.model_dump.return_value = {"id": "finding-1", "type": "CVE"}

        mock_edge = MagicMock()
        mock_edge.node = mock_node

        mock_findings = MagicMock()
        mock_findings.edges = [mock_edge]

        mock_search = MagicMock()
        mock_search.findings = mock_findings

        mock_result = MagicMock()
        mock_result.search = mock_search

        mock_gql.query_search.return_value = mock_result

        with patch("nrcli.commands.search.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.search.SearchInput") as mock_input:
                from nrcli.commands.search import run

                run(mock_client, "openssl")

                mock_input.assert_called_once()
                call_kwargs = mock_input.call_args[1]
                assert call_kwargs["query"] == "openssl"

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 1
        assert output[0]["id"] == "finding-1"

    def test_handles_empty_results(self, mock_client, capsys):
        mock_gql = MagicMock()
        mock_result = MagicMock()
        mock_result.search = None

        mock_gql.query_search.return_value = mock_result

        with patch("nrcli.commands.search.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.search.SearchInput"):
                from nrcli.commands.search import run

                run(mock_client, "nonexistent")

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output == []

    def test_outputs_csv_format(self, mock_client, capsys):
        mock_gql = MagicMock()

        mock_node = MagicMock()
        mock_node.model_dump.return_value = {"id": "finding-1", "type": "CVE"}

        mock_edge = MagicMock()
        mock_edge.node = mock_node

        mock_findings = MagicMock()
        mock_findings.edges = [mock_edge]

        mock_search = MagicMock()
        mock_search.findings = mock_findings

        mock_result = MagicMock()
        mock_result.search = mock_search

        mock_gql.query_search.return_value = mock_result

        with patch("nrcli.commands.search.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.search.SearchInput"):
                from nrcli.commands.search import run

                run(mock_client, "query", csv_format=True)

        captured = capsys.readouterr()
        assert "id" in captured.out
        assert "finding-1" in captured.out

    def test_writes_to_file(self, mock_client, tmp_path):
        mock_gql = MagicMock()

        mock_node = MagicMock()
        mock_node.model_dump.return_value = {"id": "finding-1"}

        mock_edge = MagicMock()
        mock_edge.node = mock_node

        mock_findings = MagicMock()
        mock_findings.edges = [mock_edge]

        mock_search = MagicMock()
        mock_search.findings = mock_findings

        mock_result = MagicMock()
        mock_result.search = mock_search

        mock_gql.query_search.return_value = mock_result

        output_file = tmp_path / "results.json"

        with patch("nrcli.commands.search.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.search.SearchInput"):
                from nrcli.commands.search import run

                run(mock_client, "query", output_file=str(output_file))

        content = output_file.read_text()
        output = json.loads(content)
        assert len(output) == 1
