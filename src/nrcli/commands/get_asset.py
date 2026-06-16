"""Get single asset data."""

from typing import Optional

from ..client import get_graphql_client, TurbineClient
from ..output import write_output

from netrise_turbine_sdk_graphql.input_types import AssetInput


def run(
    client: TurbineClient,
    asset_id: str,
    fields: Optional[str] = None,
    csv_format: bool = False,
    output_file: Optional[str] = None,
) -> None:
    """Get and output asset data."""
    gql = get_graphql_client(client)

    input_args = AssetInput(id=asset_id)
    result = gql.query_asset(input_args)

    if not result.asset:
        raise ValueError(f"Asset not found: {asset_id}")

    # Convert to dict for output
    asset_data = result.asset.model_dump(mode="json", exclude_none=True)

    write_output(asset_data, output_file, csv_format, fields)
