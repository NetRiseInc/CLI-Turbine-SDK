"""TurbineClient wrapper for CLI usage."""

from typing import Optional

import httpx

from .config import Config

# Import SDK modules
from netrise_turbine_sdk import TurbineClient, TurbineClientConfig


def create_client(config: Config, timeout: float = 30.0) -> TurbineClient:
    """Create a TurbineClient from CLI config."""
    sdk_config = TurbineClientConfig(
        endpoint=config.endpoint,
        domain=config.domain,
        client_id=config.client_id,
        client_secret=config.client_secret,
        audience=config.audience,
        organization_id=config.organization_id,
        turbine_api_token=config.turbine_api_token,
    )
    return TurbineClient(sdk_config, timeout=timeout)


def get_token(client: TurbineClient) -> str:
    """Get the authentication token from the client."""
    return client._get_token()


def get_graphql_client(client: TurbineClient):
    """Get the GraphQL client from TurbineClient."""
    return client.graphql()
