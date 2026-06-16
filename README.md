# nrcli - NetRise Turbine SDK CLI

Command-line interface for the NetRise Turbine SDK.

## Installation

```bash
pip install -e .
```

## Configuration

The CLI supports two configuration formats:

### .env format

```
endpoint=https://apollo.turbine.netrise.io/graphql/v3
domain=https://authn.turbine.netrise.io
client_id=xxx
client_secret=xxx
audience=https://prod.turbine.netrise.io/
organization_id=xxx
```

### YAML format

```yaml
token_url: "https://authn.turbine.netrise.io/oauth/token"
client_id: "xxx"
client_secret: "xxx"
audience: "https://prod.turbine.netrise.io/"
organization_id: "xxx"
endpoint: "https://apollo.turbine.netrise.io"
```

## Usage

```bash
# Show help
nrcli --help

# Use a specific config file
nrcli --config config.yaml <command>

# Print auth token
nrcli --config config.yaml token

# Get asset data
nrcli --config config.yaml get-asset <asset_id>
nrcli --config config.yaml get-asset <asset_id> --csv
nrcli --config config.yaml get-asset <asset_id> --data id,name,status

# Get all assets
nrcli --config config.yaml get-assets
nrcli --config config.yaml get-assets output.json
nrcli --config config.yaml get-assets --csv

# Get asset overview
nrcli --config config.yaml overview <asset_id>

# Check asset status
nrcli --config config.yaml status <asset_id>

# Submit firmware
nrcli --config config.yaml submit firmware.bin
nrcli --config config.yaml submit firmware.bin --name "My Asset" --manufacturer "Vendor"

# Update asset
nrcli --config config.yaml update <asset_id> --name "New Name"

# Search
nrcli --config config.yaml search "query string"

# Compare two assets
nrcli --config config.yaml diff <asset_id_1> <asset_id_2>

# Download files
nrcli --config config.yaml download <asset_id>
nrcli --config config.yaml download <asset_id> --type extracted

# Execute raw GraphQL
nrcli --config config.yaml gql query.graphql
nrcli --config config.yaml gql query.graphql --arguments '{"id": "xxx"}'
```

## Commands

| Command | Description |
|---------|-------------|
| `claims` | Print JWT token claims |
| `diff` | Compare two assets |
| `download` | Download firmware or extracted files |
| `get-asset` | Get single asset data |
| `get-assets` | Get all assets |
| `gql` | Execute raw GraphQL query |
| `overview` | Get asset overview summary |
| `search` | Search for firmware |
| `status` | Check asset analysis status |
| `submit` | Submit firmware for analysis |
| `token` | Print authentication token |
| `update` | Update asset metadata |
