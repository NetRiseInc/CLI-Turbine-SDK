"""Asset overview summary."""

from ..client import get_graphql_client, TurbineClient

from netrise_turbine_sdk_graphql.input_types import AssetInput


def run(client: TurbineClient, asset_id: str) -> None:
    """Print asset overview summary."""
    gql = get_graphql_client(client)

    input_args = AssetInput(id=asset_id)
    result = gql.query_asset(input_args)

    if not result.asset:
        raise ValueError(f"Asset not found: {asset_id}")

    asset = result.asset

    # Basic info
    print("=" * 60)
    print(f"ASSET OVERVIEW: {asset.name or asset_id}")
    print("=" * 60)
    print()

    print("BASIC INFORMATION")
    print("-" * 40)
    print(f"  ID:      {asset.id}")
    print(f"  Name:    {asset.name or 'N/A'}")
    print(f"  Status:  {asset.status}")

    if hasattr(asset, "vendor") and asset.vendor:
        print(f"  Vendor:  {asset.vendor}")
    if hasattr(asset, "product") and asset.product:
        print(f"  Product: {asset.product}")
    if hasattr(asset, "version") and asset.version:
        print(f"  Version: {asset.version}")

    print()

    # Analytics/Risk summary if available
    if hasattr(asset, "analytic") and asset.analytic:
        analytic = asset.analytic
        print("ANALYTICS SUMMARY")
        print("-" * 40)

        if hasattr(analytic, "risk_score"):
            print(f"  Risk Score: {analytic.risk_score}")

        if hasattr(analytic, "vulnerability_count"):
            print(f"  Vulnerabilities: {analytic.vulnerability_count}")

        if hasattr(analytic, "component_count"):
            print(f"  Components: {analytic.component_count}")

        if hasattr(analytic, "critical_count"):
            print(f"  Critical: {analytic.critical_count}")
        if hasattr(analytic, "high_count"):
            print(f"  High: {analytic.high_count}")
        if hasattr(analytic, "medium_count"):
            print(f"  Medium: {analytic.medium_count}")
        if hasattr(analytic, "low_count"):
            print(f"  Low: {analytic.low_count}")

        print()

    # Dates
    print("TIMESTAMPS")
    print("-" * 40)
    if hasattr(asset, "created_at") and asset.created_at:
        print(f"  Created:  {asset.created_at}")
    if hasattr(asset, "updated_at") and asset.updated_at:
        print(f"  Updated:  {asset.updated_at}")

    print()
