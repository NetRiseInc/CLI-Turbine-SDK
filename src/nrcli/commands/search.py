"""Search for firmware."""

from typing import Optional

from ..client import get_graphql_client, TurbineClient
from ..output import write_output

from netrise_turbine_sdk_graphql.input_types import SearchInput
from netrise_turbine_sdk_graphql.enums import ArtifactName


# Default artifacts to search across
DEFAULT_ARTIFACTS = [
    ArtifactName.ALL_COMPONENT_CVES,
    ArtifactName.CERTIFICATE,
    ArtifactName.BINARY_PROTECTIONS,
]


def run(
    client: TurbineClient,
    query: str,
    csv_format: bool = False,
    output_file: Optional[str] = None,
) -> None:
    """Search for assets and output results."""
    gql = get_graphql_client(client)

    input_args = SearchInput(
        query=query,
        artifacts=DEFAULT_ARTIFACTS,
    )
    result = gql.query_search(input_args)

    # Extract search results from findings edges
    results = []
    if result.search and result.search.findings:
        for edge in result.search.findings.edges:
            if edge.node:
                results.append(edge.node.model_dump(mode="json", exclude_none=True))

    write_output(results, output_file, csv_format)
