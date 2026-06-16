"""Update asset metadata."""

import json
from typing import Optional

from ..client import get_graphql_client, TurbineClient

from netrise_turbine_sdk_graphql.input_types import UpdateAssetInput


def run(
    client: TurbineClient,
    asset_id: str,
    name: Optional[str] = None,
    vendor: Optional[str] = None,
    product: Optional[str] = None,
    version: Optional[str] = None,
) -> None:
    """Update asset metadata."""
    gql = get_graphql_client(client)

    # Build input with only provided fields
    input_args = UpdateAssetInput(
        id=asset_id,
        name=name,
        vendor=vendor,
        product=product,
        version=version,
    )

    result = gql.mutation_asset_update(input_args)

    # Output result
    if result.asset_update:
        asset = result.asset_update
        output = asset.model_dump(mode="json", exclude_none=True)
        print(json.dumps(output, indent=2))
    else:
        print(f"Asset {asset_id} updated successfully")
