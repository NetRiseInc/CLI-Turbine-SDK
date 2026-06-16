"""Check asset analysis status."""

from ..client import get_graphql_client, TurbineClient

from netrise_turbine_sdk_graphql.input_types import AssetInput


def run(client: TurbineClient, asset_id: str) -> None:
    """Print asset analysis status."""
    gql = get_graphql_client(client)

    input_args = AssetInput(id=asset_id)
    result = gql.query_asset(input_args)

    asset = result.asset
    status = asset.status if asset else "Unknown"

    print(f"Asset ID: {asset_id}")
    print(f"Status: {status}")

    if asset:
        if hasattr(asset, "name") and asset.name:
            print(f"Name: {asset.name}")
        if hasattr(asset, "processing_status") and asset.processing_status:
            print(f"Processing Status: {asset.processing_status}")
