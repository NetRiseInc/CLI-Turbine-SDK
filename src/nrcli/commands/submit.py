"""Submit firmware for analysis."""

import json
from pathlib import Path
from typing import Optional

from ..client import get_graphql_client, TurbineClient

from netrise_turbine_sdk_graphql.input_types import SubmitAssetInput


def run(
    client: TurbineClient,
    path: str,
    name: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    version: Optional[str] = None,
) -> None:
    """Submit firmware file for analysis."""
    filepath = Path(path)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not filepath.is_file():
        raise ValueError(f"Not a file: {path}")

    # Use filename as default name
    asset_name = name or filepath.name

    gql = get_graphql_client(client)

    # Build input
    input_args = SubmitAssetInput(
        name=asset_name,
        manufacturer=manufacturer,
        model=model,
        version=version,
    )

    # Submit with file upload
    with open(filepath, "rb") as f:
        result = gql.mutation_asset_submit(
            submit_asset_args=input_args,
            file=f,
        )

    # Output result
    if result.asset_submit:
        asset = result.asset_submit
        output = {
            "id": asset.id,
            "name": getattr(asset, "name", None),
            "status": getattr(asset, "status", None),
        }
        print(json.dumps(output, indent=2))
    else:
        print("Asset submitted successfully")
