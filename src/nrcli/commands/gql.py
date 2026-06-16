"""Execute raw GraphQL queries."""

import json
import sys
from pathlib import Path
from typing import Optional

from ..client import get_graphql_client, TurbineClient


def run(
    client: TurbineClient,
    input_path: str,
    output_path: Optional[str] = None,
    arguments: Optional[str] = None,
) -> None:
    """Execute a raw GraphQL query."""
    # Read query from file or stdin
    if input_path == "-":
        query = sys.stdin.read()
    else:
        query_file = Path(input_path)
        if not query_file.exists():
            raise FileNotFoundError(f"Query file not found: {input_path}")
        query = query_file.read_text()

    # Parse variables if provided
    variables = {}
    if arguments:
        try:
            variables = json.loads(arguments)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON arguments: {e}")

    # Execute query
    gql = get_graphql_client(client)
    response = gql.execute(query=query, operation_name=None, variables=variables)
    data = gql.get_data(response)

    # Format output
    output = json.dumps(data, indent=2, default=str)

    # Write output
    if output_path:
        Path(output_path).write_text(output)
        print(f"Output written to: {output_path}")
    else:
        print(output)
