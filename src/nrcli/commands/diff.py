"""Compare two assets."""

import json
from typing import Any

from ..client import get_graphql_client, TurbineClient

from netrise_turbine_sdk_graphql.input_types import AssetInput


def dict_diff(d1: dict, d2: dict, path: str = "") -> list[dict]:
    """Compare two dictionaries and return differences."""
    diffs = []

    all_keys = set(d1.keys()) | set(d2.keys())

    for key in sorted(all_keys):
        current_path = f"{path}.{key}" if path else key
        v1 = d1.get(key)
        v2 = d2.get(key)

        if key not in d1:
            diffs.append({
                "path": current_path,
                "type": "added",
                "value": v2,
            })
        elif key not in d2:
            diffs.append({
                "path": current_path,
                "type": "removed",
                "value": v1,
            })
        elif isinstance(v1, dict) and isinstance(v2, dict):
            diffs.extend(dict_diff(v1, v2, current_path))
        elif v1 != v2:
            diffs.append({
                "path": current_path,
                "type": "changed",
                "from": v1,
                "to": v2,
            })

    return diffs


def run(client: TurbineClient, asset_id_1: str, asset_id_2: str) -> None:
    """Compare two assets and show differences."""
    gql = get_graphql_client(client)

    # Fetch both assets
    input1 = AssetInput(id=asset_id_1)
    input2 = AssetInput(id=asset_id_2)

    result1 = gql.query_asset(input1)
    result2 = gql.query_asset(input2)

    if not result1.asset:
        raise ValueError(f"Asset not found: {asset_id_1}")
    if not result2.asset:
        raise ValueError(f"Asset not found: {asset_id_2}")

    # Convert to dicts
    asset1 = result1.asset.model_dump(mode="json", exclude_none=True)
    asset2 = result2.asset.model_dump(mode="json", exclude_none=True)

    # Compare
    diffs = dict_diff(asset1, asset2)

    if not diffs:
        print("No differences found between assets.")
        return

    # Output
    print(f"Comparing: {asset_id_1} vs {asset_id_2}")
    print("=" * 60)
    print()

    for diff in diffs:
        path = diff["path"]
        diff_type = diff["type"]

        if diff_type == "added":
            print(f"+ {path}: {json.dumps(diff['value'], default=str)}")
        elif diff_type == "removed":
            print(f"- {path}: {json.dumps(diff['value'], default=str)}")
        elif diff_type == "changed":
            print(f"~ {path}:")
            print(f"    from: {json.dumps(diff['from'], default=str)}")
            print(f"    to:   {json.dumps(diff['to'], default=str)}")

    print()
    print(f"Total differences: {len(diffs)}")
