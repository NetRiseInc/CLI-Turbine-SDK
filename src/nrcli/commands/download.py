"""Download firmware or extracted files."""

from pathlib import Path
from typing import Optional

import httpx

from ..client import get_graphql_client, get_token, TurbineClient

from netrise_turbine_sdk_graphql.input_types import (
    FirmwareDownloadInput,
    ExtractedFirmwareDownloadInput,
)


def run(
    client: TurbineClient,
    asset_id: str,
    download_type: str = "firmware",
    output_path: Optional[str] = None,
) -> None:
    """Download asset data."""
    gql = get_graphql_client(client)

    # Get download URLs based on type
    if download_type == "firmware":
        input_args = FirmwareDownloadInput(asset_id=asset_id)
        result = gql.query_download_firmware(input_args)
        if result.download and result.download.firmware:
            urls = result.download.firmware.download_urls_list or []
        else:
            urls = []
        default_ext = ".bin"
    elif download_type == "extracted":
        input_args = ExtractedFirmwareDownloadInput(asset_id=asset_id)
        result = gql.query_download_extracted_firmware(input_args)
        if result.download and result.download.extracted_firmware:
            urls = result.download.extracted_firmware.download_urls_list or []
        else:
            urls = []
        default_ext = ".tar.gz"
    else:
        raise ValueError(f"Unknown download type: {download_type}. Use 'firmware' or 'extracted'.")

    # Filter out None values
    download_urls = [u for u in urls if u]

    if not download_urls:
        raise ValueError(f"No download URL available for {download_type}")

    # Use first URL
    download_url = download_urls[0]

    # Determine output path
    if output_path:
        out_path = Path(output_path)
    else:
        out_path = Path(f"{asset_id}_{download_type}{default_ext}")

    # Download the file
    print(f"Downloading {download_type} to {out_path}...")

    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with httpx.Client() as http_client:
        with http_client.stream("GET", download_url, headers=headers, follow_redirects=True) as response:
            response.raise_for_status()

            total = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(out_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = (downloaded / total) * 100
                        print(f"\r  Progress: {pct:.1f}%", end="", flush=True)

    print()
    print(f"Downloaded to: {out_path}")
