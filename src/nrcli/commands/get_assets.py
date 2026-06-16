"""Get all assets data with pagination."""

from typing import Optional

from ..client import get_graphql_client, TurbineClient
from ..output import write_output

from netrise_turbine_sdk_graphql.input_types import AssetsRelayInput, Cursor


def run(
    client: TurbineClient,
    output_file: Optional[str] = None,
    fields: Optional[str] = None,
    csv_format: bool = False,
    limit: int = 100,
) -> None:
    """Get all assets with pagination and output them."""
    gql = get_graphql_client(client)

    all_assets = []
    cursor = None

    while True:
        input_args = AssetsRelayInput(
            cursor=Cursor(after=cursor) if cursor else Cursor(),
            limit=limit,
        )

        result = gql.query_assets_relay(input_args)

        # Extract assets from edges
        if result.assets_relay and result.assets_relay.edges:
            for edge in result.assets_relay.edges:
                if edge.node:
                    asset_data = edge.node.model_dump(mode="json", exclude_none=True)
                    all_assets.append(asset_data)

            # Check for next page
            page_info = result.assets_relay.page_info
            if page_info and page_info.has_next_page and result.assets_relay.edges:
                cursor = result.assets_relay.edges[-1].cursor
            else:
                break
        else:
            break

    write_output(all_assets, output_file, csv_format, fields)
