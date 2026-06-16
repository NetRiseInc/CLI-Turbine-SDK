import pytest
from unittest.mock import patch, MagicMock


class TestStatusCommand:
    def test_prints_asset_status(self, mock_client, mock_asset, capsys):
        mock_gql = MagicMock()
        mock_result = MagicMock()
        mock_result.asset = mock_asset

        mock_gql.query_asset.return_value = mock_result

        with patch("nrcli.commands.status.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.status.AssetInput") as mock_input:
                from nrcli.commands.status import run

                run(mock_client, "test-asset-id")

                mock_input.assert_called_once_with(id="test-asset-id")
                mock_gql.query_asset.assert_called_once()

        captured = capsys.readouterr()
        assert "Asset ID: test-asset-id" in captured.out
        assert "Status: COMPLETE" in captured.out

    def test_prints_unknown_when_asset_not_found(self, mock_client, capsys):
        mock_gql = MagicMock()
        mock_result = MagicMock()
        mock_result.asset = None

        mock_gql.query_asset.return_value = mock_result

        with patch("nrcli.commands.status.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.status.AssetInput"):
                from nrcli.commands.status import run

                run(mock_client, "nonexistent-id")

        captured = capsys.readouterr()
        assert "Status: Unknown" in captured.out

    def test_prints_optional_fields_when_present(self, mock_client, capsys):
        mock_gql = MagicMock()
        mock_asset = MagicMock()
        mock_asset.status = "PROCESSING"
        mock_asset.name = "firmware.bin"
        mock_asset.processing_status = "EXTRACTING"

        mock_result = MagicMock()
        mock_result.asset = mock_asset

        mock_gql.query_asset.return_value = mock_result

        with patch("nrcli.commands.status.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.status.AssetInput"):
                from nrcli.commands.status import run

                run(mock_client, "test-id")

        captured = capsys.readouterr()
        assert "Name: firmware.bin" in captured.out
        assert "Processing Status: EXTRACTING" in captured.out
