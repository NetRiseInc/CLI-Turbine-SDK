"""Main entry point for nrcli."""

import argparse
import sys

from .config import load_config
from .client import create_client


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="nrcli",
        description="NetRise Turbine SDK CLI",
    )

    # Global options
    parser.add_argument(
        "--config",
        "-c",
        metavar="FILE",
        help="Path to config file (.env or .yaml)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30)",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # claims command
    claims_parser = subparsers.add_parser("claims", help="Print JWT token claims")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Compare two assets")
    diff_parser.add_argument("--asset_id_1", required=True, help="First asset ID")
    diff_parser.add_argument("--asset_id_2", required=True, help="Second asset ID")

    # download command
    download_parser = subparsers.add_parser(
        "download", help="Download firmware or extracted files"
    )
    download_parser.add_argument("--asset_id", required=True, help="Asset ID")
    download_parser.add_argument(
        "--type",
        "-t",
        choices=["firmware", "extracted"],
        default="firmware",
        help="Type of download (default: firmware)",
    )
    download_parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Output file path",
    )

    # get-asset command
    get_asset_parser = subparsers.add_parser("get-asset", help="Get asset data")
    get_asset_parser.add_argument("--asset_id", required=True, help="Asset ID")
    get_asset_parser.add_argument(
        "--data",
        "-d",
        metavar="FIELDS",
        help="Comma-separated list of fields to include",
    )
    get_asset_parser.add_argument(
        "--csv",
        action="store_true",
        help="Output in CSV format",
    )
    get_asset_parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Output file path",
    )

    # get-assets command
    get_assets_parser = subparsers.add_parser("get-assets", help="Get all assets")
    get_assets_parser.add_argument(
        "output_file",
        nargs="?",
        help="Output file path (optional, defaults to stdout)",
    )
    get_assets_parser.add_argument(
        "--data",
        "-d",
        metavar="FIELDS",
        help="Comma-separated list of fields to include",
    )
    get_assets_parser.add_argument(
        "--csv",
        action="store_true",
        help="Output in CSV format",
    )
    get_assets_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=100,
        help="Number of assets per page (default: 100)",
    )

    # gql command
    gql_parser = subparsers.add_parser("gql", help="Execute raw GraphQL query")
    gql_parser.add_argument("input", help="GraphQL query file or '-' for stdin")
    gql_parser.add_argument("output", nargs="?", help="Output file path")
    gql_parser.add_argument(
        "--arguments",
        "-a",
        metavar="JSON",
        help="JSON string of query variables",
    )

    # overview command
    overview_parser = subparsers.add_parser("overview", help="Get asset overview summary")
    overview_parser.add_argument("--asset_id", required=True, help="Asset ID")

    # search command
    search_parser = subparsers.add_parser("search", help="Search for firmware")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--csv",
        action="store_true",
        help="Output in CSV format",
    )
    search_parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Output file path",
    )

    # status command
    status_parser = subparsers.add_parser("status", help="Check asset analysis status")
    status_parser.add_argument("--asset_id", required=True, help="Asset ID")

    # submit command
    submit_parser = subparsers.add_parser("submit", help="Submit firmware for analysis")
    submit_parser.add_argument("path", help="Path to firmware file")
    submit_parser.add_argument("--name", "-n", help="Asset name")
    submit_parser.add_argument("--manufacturer", help="Manufacturer name")
    submit_parser.add_argument("--model", help="Model name")
    submit_parser.add_argument("--version", help="Version string")

    # token command
    token_parser = subparsers.add_parser("token", help="Print authentication token")

    # update command
    update_parser = subparsers.add_parser("update", help="Update asset metadata")
    update_parser.add_argument("--asset_id", required=True, help="Asset ID")
    update_parser.add_argument("--name", "-n", help="New asset name")
    update_parser.add_argument("--vendor", help="New vendor name")
    update_parser.add_argument("--product", help="New product name")
    update_parser.add_argument("--version", help="New version string")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load config and create client
    try:
        config = load_config(args.config)
        client = create_client(config, timeout=args.timeout)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)

    # Dispatch to command handler
    try:
        if args.command == "claims":
            from .commands.claims import run
            run(client)
        elif args.command == "diff":
            from .commands.diff import run
            run(client, args.asset_id_1, args.asset_id_2)
        elif args.command == "download":
            from .commands.download import run
            run(client, args.asset_id, args.type, args.output)
        elif args.command == "get-asset":
            from .commands.get_asset import run
            run(client, args.asset_id, args.data, args.csv, args.output)
        elif args.command == "get-assets":
            from .commands.get_assets import run
            run(client, args.output_file, args.data, args.csv, args.limit)
        elif args.command == "gql":
            from .commands.gql import run
            run(client, args.input, args.output, args.arguments)
        elif args.command == "overview":
            from .commands.overview import run
            run(client, args.asset_id)
        elif args.command == "search":
            from .commands.search import run
            run(client, args.query, args.csv, args.output)
        elif args.command == "status":
            from .commands.status import run
            run(client, args.asset_id)
        elif args.command == "submit":
            from .commands.submit import run
            run(
                client,
                args.path,
                name=args.name,
                manufacturer=args.manufacturer,
                model=args.model,
                version=args.version,
            )
        elif args.command == "token":
            from .commands.token import run
            run(client)
        elif args.command == "update":
            from .commands.update import run
            run(
                client,
                args.asset_id,
                name=args.name,
                vendor=args.vendor,
                product=args.product,
                version=args.version,
            )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
