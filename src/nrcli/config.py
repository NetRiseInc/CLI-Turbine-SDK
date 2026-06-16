"""Configuration loading for nrcli.

Supports both .env and YAML config formats.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from dotenv import dotenv_values


@dataclass
class Config:
    """CLI configuration."""

    endpoint: str
    domain: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    audience: Optional[str] = None
    organization_id: Optional[str] = None
    turbine_api_token: Optional[str] = None

    @classmethod
    def from_env_file(cls, path: Path) -> "Config":
        """Load config from .env file."""
        values = dotenv_values(path)
        return cls(
            endpoint=values.get("endpoint", ""),
            domain=values.get("domain"),
            client_id=values.get("client_id"),
            client_secret=values.get("client_secret"),
            audience=values.get("audience"),
            organization_id=values.get("organization_id"),
            turbine_api_token=values.get("turbine_api_token"),
        )

    @classmethod
    def from_yaml_file(cls, path: Path) -> "Config":
        """Load config from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)

        # Handle token_url -> domain conversion
        domain = data.get("domain")
        if not domain and data.get("token_url"):
            # Extract domain from token_url (e.g., https://authn.turbine.netrise.io/oauth/token)
            token_url = data["token_url"]
            if "/oauth/token" in token_url:
                domain = token_url.replace("/oauth/token", "")

        return cls(
            endpoint=data.get("endpoint", ""),
            domain=domain,
            client_id=data.get("client_id"),
            client_secret=data.get("client_secret"),
            audience=data.get("audience"),
            organization_id=data.get("organization_id"),
            turbine_api_token=data.get("turbine_api_token"),
        )

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load config from file, auto-detecting format by extension."""
        suffix = path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            return cls.from_yaml_file(path)
        else:
            # Default to .env format
            return cls.from_env_file(path)

    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables."""
        return cls(
            endpoint=os.environ.get("TURBINE_ENDPOINT", ""),
            domain=os.environ.get("TURBINE_DOMAIN"),
            client_id=os.environ.get("TURBINE_CLIENT_ID"),
            client_secret=os.environ.get("TURBINE_CLIENT_SECRET"),
            audience=os.environ.get("TURBINE_AUDIENCE"),
            organization_id=os.environ.get("TURBINE_ORGANIZATION_ID"),
            turbine_api_token=os.environ.get("TURBINE_API_TOKEN"),
        )


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or environment.

    Priority:
    1. Explicit config file path (--config)
    2. Environment variables
    """
    if config_path:
        return Config.from_file(Path(config_path))
    return Config.from_env()
