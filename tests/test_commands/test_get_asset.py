import json
import pytest
from unittest.mock import patch, MagicMock


class TestGetAssetCommand:
    def test_outputs_asset_as_json(self, mock_client, mock_asset, capsys):
        mock_gql = MagicMock()
        mock_result = MagicMock()
        mock_result.asset = mock_asset

        mock_gql.query_asset.return_value = mock_result

        with patch("nrcli.commands.get_asset.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_asset.AssetInput") as mock_input:
                from nrcli.commands.get_asset import run

                run(mock_client, "test-asset-id")

                mock_input.assert_called_once_with(id="test-asset-id")

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["id"] == "test-asset-id"
        assert output["name"] == "test-firmware.bin"

    def test_raises_when_asset_not_found(self, mock_client):
        mock_gql = MagicMock()
        mock_result = MagicMock()
        mock_result.asset = None

        mock_gql.query_asset.return_value = mock_result

        with patch("nrcli.commands.get_asset.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_asset.AssetInput"):
                from nrcli.commands.get_asset import run

                with pytest.raises(ValueError, match="Asset not found"):
                    run(mock_client, "nonexistent-id")

    def test_outputs_csv_format(self, mock_client, mock_asset, capsys):
        mock_gql = MagicMock()
        mock_result = MagicMock()
        mock_result.asset = mock_asset

        mock_gql.query_asset.return_value = mock_result

        with patch("nrcli.commands.get_asset.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_asset.AssetInput"):
                from nrcli.commands.get_asset import run

                run(mock_client, "test-asset-id", csv_format=True)

        captured = capsys.readouterr()
        assert "id" in captured.out
        assert "test-asset-id" in captured.out

    def test_filters_fields(self, mock_client, mock_asset, capsys):
        mock_gql = MagicMock()
        mock_result = MagicMock()
        mock_result.asset = mock_asset

        mock_gql.query_asset.return_value = mock_result

        with patch("nrcli.commands.get_asset.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_asset.AssetInput"):
                from nrcli.commands.get_asset import run

                run(mock_client, "test-asset-id", fields="id,status")

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "id" in output
        assert "status" in output
        assert "name" not in output

    def test_writes_to_file(self, mock_client, mock_asset, tmp_path):
        mock_gql = MagicMock()
        mock_result = MagicMock()
        mock_result.asset = mock_asset

        mock_gql.query_asset.return_value = mock_result

        output_file = tmp_path / "output.json"

        with patch("nrcli.commands.get_asset.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.get_asset.AssetInput"):
                from nrcli.commands.get_asset import run

                run(mock_client, "test-asset-id", output_file=str(output_file))

        content = output_file.read_text()
        output = json.loads(content)
        assert output["id"] == "test-asset-id"
