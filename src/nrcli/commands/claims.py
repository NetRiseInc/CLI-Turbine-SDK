"""Decode and print JWT token claims."""

import base64
import json

from ..client import get_token, TurbineClient


def decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verification."""
    # JWT format: header.payload.signature
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format")

    # Decode payload (second part)
    payload = parts[1]

    # Add padding if needed
    padding = 4 - len(payload) % 4
    if padding != 4:
        payload += "=" * padding

    decoded = base64.urlsafe_b64decode(payload)
    return json.loads(decoded)


def run(client: TurbineClient) -> None:
    """Print decoded JWT claims."""
    token = get_token(client)
    claims = decode_jwt_payload(token)
    print(json.dumps(claims, indent=2))
