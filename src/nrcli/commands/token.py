"""Print authentication token."""

from ..client import get_token, TurbineClient


def run(client: TurbineClient) -> None:
    """Print the authentication token."""
    token = get_token(client)
    print(token)
