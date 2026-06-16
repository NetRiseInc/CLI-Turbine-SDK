import json
import pytest
from unittest.mock import patch, MagicMock


class TestGetAssetsCommand:
    def _make_mock_page(self, assets, has_next=False, end_cursor=None):
        mock_edges = []
        for i, asset in enumerate(assets):
            mock_node = MagicMock()
            mock_node.model_dump.return_value = asset
            mock_edge = MagicMock()
            mock_edge.node = mock_node
            mock_edge.cursor = f"cursor-{i}"
            mock_edges.append(mock_edge)

        mock_page_info = MagicMock()
        mock_page_info.has_next_page = has_next

        mock_assets_relay = MagicMock()
        mock_assets_relay.edges = mock_edges
        mock_assets_relay.page_info = mock_page_info

        mock_result = MagicMock()
        mock_result.assets_relay = mock_assets_relay
        return mock_result

    def test_outputs_all_assets(self, mock_client, capsys):
        mock_gql = MagicMock()
        mock_result = self._make_mock_page([
            {"id": "asset-1", "name": "firmware1.bin"},
            {"id": "asset-2", "name": "firmware2.bin"},
        ])

        mock_gql.query_assets_relay.return_value = mock_result

        with patch("nrcli.commands.get_assets.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_assets.AssetsRelayInput"):
                with patch("nrcli.commands.get_assets.Cursor"):
                    from nrcli.commands.get_assets import run

                    run(mock_client, None)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 2
        assert output[0]["id"] == "asset-1"
        assert output[1]["id"] == "asset-2"

    def test_paginates_through_results(self, mock_client, capsys):
        mock_gql = MagicMock()

        page1 = self._make_mock_page(
            [{"id": "asset-1"}],
            has_next=True,
        )
        page2 = self._make_mock_page(
            [{"id": "asset-2"}],
            has_next=False
        )

        mock_gql.query_assets_relay.side_effect = [page1, page2]

        with patch("nrcli.commands.get_assets.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_assets.AssetsRelayInput"):
                with patch("nrcli.commands.get_assets.Cursor"):
                    from nrcli.commands.get_assets import run

                    run(mock_client, None, limit=1)

                    assert mock_gql.query_assets_relay.call_count == 2

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert len(output) == 2

    def test_respects_limit(self, mock_client):
        mock_gql = MagicMock()
        mock_result = self._make_mock_page([{"id": "asset-1"}])

        mock_gql.query_assets_relay.return_value = mock_result

        with patch("nrcli.commands.get_assets.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_assets.AssetsRelayInput") as mock_input:
                with patch("nrcli.commands.get_assets.Cursor"):
                    from nrcli.commands.get_assets import run

                    run(mock_client, None, limit=50)

                    call_kwargs = mock_input.call_args[1]
                    assert call_kwargs["limit"] == 50

    def test_outputs_csv_format(self, mock_client, capsys):
        mock_gql = MagicMock()
        mock_result = self._make_mock_page([
            {"id": "asset-1", "name": "test.bin"},
        ])

        mock_gql.query_assets_relay.return_value = mock_result

        with patch("nrcli.commands.get_assets.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_assets.AssetsRelayInput"):
                with patch("nrcli.commands.get_assets.Cursor"):
                    from nrcli.commands.get_assets import run

                    run(mock_client, None, csv_format=True)

        captured = capsys.readouterr()
        assert "id" in captured.out
        assert "asset-1" in captured.out

    def test_writes_to_file(self, mock_client, tmp_path):
        mock_gql = MagicMock()
        mock_result = self._make_mock_page([{"id": "asset-1"}])

        mock_gql.query_assets_relay.return_value = mock_result

        output_file = tmp_path / "assets.json"

        with patch("nrcli.commands.get_assets.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_assets.AssetsRelayInput"):
                with patch("nrcli.commands.get_assets.Cursor"):
                    from nrcli.commands.get_assets import run

                    run(mock_client, str(output_file))

        content = output_file.read_text()
        output = json.loads(content)
        assert len(output) == 1

    def test_filters_fields(self, mock_client, capsys):
        mock_gql = MagicMock()
        mock_result = self._make_mock_page([
            {"id": "asset-1", "name": "test.bin", "status": "COMPLETE"},
        ])

        mock_gql.query_assets_relay.return_value = mock_result

        with patch("nrcli.commands.get_assets.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_assets.AssetsRelayInput"):
                with patch("nrcli.commands.get_assets.Cursor"):
                    from nrcli.commands.get_assets import run

                    run(mock_client, None, fields="id,status")

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "id" in output[0]
        assert "status" in output[0]
        assert "name" not in output[0]

    def test_handles_empty_results(self, mock_client, capsys):
        mock_gql = MagicMock()
        mock_result = MagicMock()
        mock_result.assets_relay = None

        mock_gql.query_assets_relay.return_value = mock_result

        with patch("nrcli.commands.get_assets.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_assets.AssetsRelayInput"):
                with patch("nrcli.commands.get_assets.Cursor"):
                    from nrcli.commands.get_assets import run

                    run(mock_client, None)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output == []
