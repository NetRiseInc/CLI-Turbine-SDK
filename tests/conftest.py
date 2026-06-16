import pytest
from unittest.mock import MagicMock, PropertyMock
from nrcli.config import Config


@pytest.fixture
def mock_config():
    return Config(
        endpoint="https://apollo.turbine.netrise.io/graphql/v3",
        domain="https://authn.turbine.netrise.io",
        client_id="test-client-id",
        client_secret="test-client-secret",
        audience="https://api.turbine.netrise.io",
        organization_id="test-org-id",
    )


@pytest.fixture
def mock_client(mock_config):
    client = MagicMock()
    client._get_token.return_value = (
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0."
        "signature"
    )
    return client


@pytest.fixture
def mock_graphql_client():
    return MagicMock()


@pytest.fixture
def mock_asset():
    asset = MagicMock()
    asset.id = "test-asset-id"
    asset.name = "test-firmware.bin"
    asset.status = "COMPLETE"
    asset.processing_status = "DONE"
    asset.model_dump.return_value = {
        "id": "test-asset-id",
        "name": "test-firmware.bin",
        "status": "COMPLETE",
    }
    return asset
