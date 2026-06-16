import pytest
import sys
from unittest.mock import patch, MagicMock
from nrcli.main import main


class TestArgumentParsing:
    def test_no_command_shows_help(self, capsys):
        with patch.object(sys, "argv", ["nrcli"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_help_flag(self, capsys):
        with patch.object(sys, "argv", ["nrcli", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        output = capsys.readouterr().out
        assert "NetRise Turbine SDK CLI" in output

    def test_global_config_option(self):
        with patch.object(sys, "argv", ["nrcli", "--config", "/path/to/config.yaml", "token"]):
            with patch("nrcli.main.load_config") as mock_load:
                with patch("nrcli.main.create_client"):
                    with patch("nrcli.commands.token.run"):
                        mock_load.return_value = MagicMock()
                        main()
                        mock_load.assert_called_once_with("/path/to/config.yaml")

    def test_global_timeout_option(self):
        with patch.object(sys, "argv", ["nrcli", "--timeout", "60", "token"]):
            with patch("nrcli.main.load_config") as mock_load:
                with patch("nrcli.main.create_client") as mock_create:
                    with patch("nrcli.commands.token.run"):
                        mock_load.return_value = MagicMock()
                        mock_create.return_value = MagicMock()
                        main()
                        mock_create.assert_called_once()
                        _, kwargs = mock_create.call_args
                        assert kwargs["timeout"] == 60.0


class TestCommandDispatch:
    @pytest.fixture
    def mock_setup(self):
        with patch("nrcli.main.load_config") as mock_load:
            with patch("nrcli.main.create_client") as mock_create:
                mock_load.return_value = MagicMock()
                mock_create.return_value = MagicMock()
                yield {"load_config": mock_load, "create_client": mock_create}

    def test_token_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "token"]):
            with patch("nrcli.commands.token.run") as mock_run:
                main()
                mock_run.assert_called_once()

    def test_claims_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "claims"]):
            with patch("nrcli.commands.claims.run") as mock_run:
                main()
                mock_run.assert_called_once()

    def test_get_asset_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "get-asset", "--asset_id", "abc-123"]):
            with patch("nrcli.commands.get_asset.run") as mock_run:
                main()
                mock_run.assert_called_once()
                args = mock_run.call_args[0]
                assert args[1] == "abc-123"

    def test_get_assets_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "get-assets", "--limit", "50"]):
            with patch("nrcli.commands.get_assets.run") as mock_run:
                main()
                mock_run.assert_called_once()
                args = mock_run.call_args[0]
                assert args[4] == 50

    def test_search_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "search", "vulnerabilities"]):
            with patch("nrcli.commands.search.run") as mock_run:
                main()
                mock_run.assert_called_once()
                args = mock_run.call_args[0]
                assert args[1] == "vulnerabilities"

    def test_status_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "status", "--asset_id", "xyz-789"]):
            with patch("nrcli.commands.status.run") as mock_run:
                main()
                mock_run.assert_called_once()
                args = mock_run.call_args[0]
                assert args[1] == "xyz-789"

    def test_submit_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "submit", "/path/to/firmware.bin", "--name", "MyFirmware"]):
            with patch("nrcli.commands.submit.run") as mock_run:
                main()
                mock_run.assert_called_once()
                args, kwargs = mock_run.call_args
                assert args[1] == "/path/to/firmware.bin"
                assert kwargs["name"] == "MyFirmware"

    def test_update_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "update", "--asset_id", "abc", "--name", "NewName"]):
            with patch("nrcli.commands.update.run") as mock_run:
                main()
                mock_run.assert_called_once()
                args, kwargs = mock_run.call_args
                assert args[1] == "abc"
                assert kwargs["name"] == "NewName"

    def test_diff_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "diff", "--asset_id_1", "a1", "--asset_id_2", "a2"]):
            with patch("nrcli.commands.diff.run") as mock_run:
                main()
                mock_run.assert_called_once()
                args = mock_run.call_args[0]
                assert args[1] == "a1"
                assert args[2] == "a2"

    def test_download_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "download", "--asset_id", "abc", "--type", "extracted"]):
            with patch("nrcli.commands.download.run") as mock_run:
                main()
                mock_run.assert_called_once()
                args = mock_run.call_args[0]
                assert args[1] == "abc"
                assert args[2] == "extracted"

    def test_overview_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "overview", "--asset_id", "abc"]):
            with patch("nrcli.commands.overview.run") as mock_run:
                main()
                mock_run.assert_called_once()
                args = mock_run.call_args[0]
                assert args[1] == "abc"

    def test_gql_command(self, mock_setup):
        with patch.object(sys, "argv", ["nrcli", "gql", "query.graphql", "output.json"]):
            with patch("nrcli.commands.gql.run") as mock_run:
                main()
                mock_run.assert_called_once()
                args = mock_run.call_args[0]
                assert args[1] == "query.graphql"
                assert args[2] == "output.json"


class TestErrorHandling:
    def test_config_error_exits_with_1(self, capsys):
        with patch.object(sys, "argv", ["nrcli", "token"]):
            with patch("nrcli.main.load_config") as mock_load:
                mock_load.side_effect = Exception("Config file not found")
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

        output = capsys.readouterr().err
        assert "Error loading config" in output

    def test_command_error_exits_with_1(self, capsys):
        with patch.object(sys, "argv", ["nrcli", "token"]):
            with patch("nrcli.main.load_config") as mock_load:
                with patch("nrcli.main.create_client") as mock_create:
                    with patch("nrcli.commands.token.run") as mock_run:
                        mock_load.return_value = MagicMock()
                        mock_create.return_value = MagicMock()
                        mock_run.side_effect = Exception("API error")
                        with pytest.raises(SystemExit) as exc_info:
                            main()
                        assert exc_info.value.code == 1

        output = capsys.readouterr().err
        assert "Error:" in output
