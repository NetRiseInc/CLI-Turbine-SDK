import json
import pytest
from unittest.mock import patch, MagicMock


class TestSubmitCommand:
    def test_submits_file(self, mock_client, tmp_path, capsys):
        firmware_file = tmp_path / "firmware.bin"
        firmware_file.write_bytes(b"fake firmware content")

        mock_gql = MagicMock()
        mock_asset = MagicMock()
        mock_asset.id = "new-asset-id"
        mock_asset.name = "firmware.bin"
        mock_asset.status = "PENDING"

        mock_result = MagicMock()
        mock_result.asset_submit = mock_asset

        mock_gql.mutation_asset_submit.return_value = mock_result

        with patch("nrcli.commands.submit.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.submit.SubmitAssetInput") as mock_input:
                from nrcli.commands.submit import run

                run(mock_client, str(firmware_file))

                mock_input.assert_called_once()
                call_kwargs = mock_input.call_args[1]
                assert call_kwargs["name"] == "firmware.bin"

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["id"] == "new-asset-id"

    def test_uses_custom_name(self, mock_client, tmp_path, capsys):
        firmware_file = tmp_path / "firmware.bin"
        firmware_file.write_bytes(b"content")

        mock_gql = MagicMock()
        mock_asset = MagicMock()
        mock_asset.id = "new-id"
        mock_asset.name = "Custom Name"
        mock_asset.status = "PENDING"

        mock_result = MagicMock()
        mock_result.asset_submit = mock_asset

        mock_gql.mutation_asset_submit.return_value = mock_result

        with patch("nrcli.commands.submit.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.submit.SubmitAssetInput") as mock_input:
                from nrcli.commands.submit import run

                run(mock_client, str(firmware_file), name="Custom Name")

                call_kwargs = mock_input.call_args[1]
                assert call_kwargs["name"] == "Custom Name"

    def test_passes_metadata(self, mock_client, tmp_path):
        firmware_file = tmp_path / "firmware.bin"
        firmware_file.write_bytes(b"content")

        mock_gql = MagicMock()
        mock_asset = MagicMock()
        mock_asset.id = "new-id"
        mock_asset.name = "firmware.bin"
        mock_asset.status = "PENDING"

        mock_result = MagicMock()
        mock_result.asset_submit = mock_asset

        mock_gql.mutation_asset_submit.return_value = mock_result

        with patch("nrcli.commands.submit.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.submit.SubmitAssetInput") as mock_input:
                from nrcli.commands.submit import run

                run(
                    mock_client,
                    str(firmware_file),
                    manufacturer="Acme Corp",
                    model="Router X1",
                    version="2.0.1",
                )

                call_kwargs = mock_input.call_args[1]
                assert call_kwargs["manufacturer"] == "Acme Corp"
                assert call_kwargs["model"] == "Router X1"
                assert call_kwargs["version"] == "2.0.1"

    def test_file_not_found_raises(self, mock_client):
        from nrcli.commands.submit import run

        with pytest.raises(FileNotFoundError, match="File not found"):
            run(mock_client, "/nonexistent/path/firmware.bin")

    def test_directory_raises(self, mock_client, tmp_path):
        from nrcli.commands.submit import run

        with pytest.raises(ValueError, match="Not a file"):
            run(mock_client, str(tmp_path))

    def test_prints_success_when_no_asset_returned(self, mock_client, tmp_path, capsys):
        firmware_file = tmp_path / "firmware.bin"
        firmware_file.write_bytes(b"content")

        mock_gql = MagicMock()
        mock_result = MagicMock()
        mock_result.asset_submit = None

        mock_gql.mutation_asset_submit.return_value = mock_result

        with patch("nrcli.commands.submit.get_graphql_client", return_value=mock_gql):
            with patch("nrcli.commands.submit.SubmitAssetInput"):
                from nrcli.commands.submit import run

                run(mock_client, str(firmware_file))

        captured = capsys.readouterr()
        assert "Asset submitted successfully" in captured.out
