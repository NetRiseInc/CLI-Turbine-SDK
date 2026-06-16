import os
import pytest
from pathlib import Path
from nrcli.config import Config, load_config


class TestConfigFromEnvFile:
    def test_loads_all_fields(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "endpoint=https://example.com/graphql\n"
            "domain=https://auth.example.com\n"
            "client_id=my-client\n"
            "client_secret=my-secret\n"
            "audience=https://api.example.com\n"
            "organization_id=org-123\n"
            "turbine_api_token=token-abc\n"
        )

        config = Config.from_env_file(env_file)

        assert config.endpoint == "https://example.com/graphql"
        assert config.domain == "https://auth.example.com"
        assert config.client_id == "my-client"
        assert config.client_secret == "my-secret"
        assert config.audience == "https://api.example.com"
        assert config.organization_id == "org-123"
        assert config.turbine_api_token == "token-abc"

    def test_missing_optional_fields(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("endpoint=https://example.com/graphql\n")

        config = Config.from_env_file(env_file)

        assert config.endpoint == "https://example.com/graphql"
        assert config.domain is None
        assert config.client_id is None


class TestConfigFromYamlFile:
    def test_loads_all_fields(self, tmp_path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(
            "endpoint: https://example.com/graphql\n"
            "domain: https://auth.example.com\n"
            "client_id: my-client\n"
            "client_secret: my-secret\n"
            "audience: https://api.example.com\n"
            "organization_id: org-123\n"
        )

        config = Config.from_yaml_file(yaml_file)

        assert config.endpoint == "https://example.com/graphql"
        assert config.domain == "https://auth.example.com"
        assert config.client_id == "my-client"

    def test_converts_token_url_to_domain(self, tmp_path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(
            "endpoint: https://example.com/graphql\n"
            "token_url: https://authn.turbine.netrise.io/oauth/token\n"
            "client_id: my-client\n"
        )

        config = Config.from_yaml_file(yaml_file)

        assert config.domain == "https://authn.turbine.netrise.io"

    def test_domain_takes_precedence_over_token_url(self, tmp_path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(
            "endpoint: https://example.com/graphql\n"
            "domain: https://explicit-domain.com\n"
            "token_url: https://authn.turbine.netrise.io/oauth/token\n"
        )

        config = Config.from_yaml_file(yaml_file)

        assert config.domain == "https://explicit-domain.com"


class TestConfigFromFile:
    def test_detects_yaml_extension(self, tmp_path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("endpoint: https://example.com/graphql\n")

        config = Config.from_file(yaml_file)

        assert config.endpoint == "https://example.com/graphql"

    def test_detects_yml_extension(self, tmp_path):
        yml_file = tmp_path / "config.yml"
        yml_file.write_text("endpoint: https://example.com/graphql\n")

        config = Config.from_file(yml_file)

        assert config.endpoint == "https://example.com/graphql"

    def test_defaults_to_env_format(self, tmp_path):
        env_file = tmp_path / "config.txt"
        env_file.write_text("endpoint=https://example.com/graphql\n")

        config = Config.from_file(env_file)

        assert config.endpoint == "https://example.com/graphql"


class TestConfigFromEnv:
    def test_loads_from_environment_variables(self, monkeypatch):
        monkeypatch.setenv("TURBINE_ENDPOINT", "https://example.com/graphql")
        monkeypatch.setenv("TURBINE_DOMAIN", "https://auth.example.com")
        monkeypatch.setenv("TURBINE_CLIENT_ID", "env-client")
        monkeypatch.setenv("TURBINE_CLIENT_SECRET", "env-secret")
        monkeypatch.setenv("TURBINE_AUDIENCE", "https://api.example.com")
        monkeypatch.setenv("TURBINE_ORGANIZATION_ID", "env-org")
        monkeypatch.setenv("TURBINE_API_TOKEN", "env-token")

        config = Config.from_env()

        assert config.endpoint == "https://example.com/graphql"
        assert config.domain == "https://auth.example.com"
        assert config.client_id == "env-client"
        assert config.client_secret == "env-secret"
        assert config.audience == "https://api.example.com"
        assert config.organization_id == "env-org"
        assert config.turbine_api_token == "env-token"

    def test_missing_env_vars_return_none(self, monkeypatch):
        monkeypatch.delenv("TURBINE_ENDPOINT", raising=False)
        monkeypatch.delenv("TURBINE_DOMAIN", raising=False)

        config = Config.from_env()

        assert config.endpoint == ""
        assert config.domain is None


class TestLoadConfig:
    def test_uses_config_file_when_provided(self, tmp_path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("endpoint: https://from-file.com/graphql\n")

        config = load_config(str(yaml_file))

        assert config.endpoint == "https://from-file.com/graphql"

    def test_falls_back_to_env_when_no_file(self, monkeypatch):
        monkeypatch.setenv("TURBINE_ENDPOINT", "https://from-env.com/graphql")

        config = load_config(None)

        assert config.endpoint == "https://from-env.com/graphql"
