"""Output formatting utilities for CLI."""

import csv
import io
import json
import sys
from typing import Any, Optional, Sequence


def extract_fields(data: dict, fields: Sequence[str]) -> dict:
    """Extract specific fields from a dictionary."""
    return {k: data.get(k) for k in fields}


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Flatten a nested dictionary for CSV output."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, json.dumps(v)))
        else:
            items.append((new_key, v))
    return dict(items)


def to_json(data: Any, indent: int = 2) -> str:
    """Convert data to pretty-printed JSON string."""
    return json.dumps(data, indent=indent, default=str)


def to_csv(data: list[dict], fields: Optional[Sequence[str]] = None) -> str:
    """Convert list of dicts to CSV string.

    Args:
        data: List of dictionaries to convert
        fields: Optional list of fields to include (in order)
    """
    if not data:
        return ""

    # Flatten nested dictionaries
    flat_data = [flatten_dict(d) for d in data]

    # Determine fieldnames
    if fields:
        fieldnames = list(fields)
    else:
        # Get all unique keys while preserving order
        fieldnames = []
        for row in flat_data:
            for key in row.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(flat_data)
    return output.getvalue()


def format_output(
    data: Any,
    csv_format: bool = False,
    fields: Optional[str] = None,
) -> str:
    """Format data for output.

    Args:
        data: Data to format (dict or list of dicts)
        csv_format: If True, output CSV instead of JSON
        fields: Comma-separated list of fields to include
    """
    field_list = fields.split(",") if fields else None

    # Handle single dict - wrap in list for CSV
    if isinstance(data, dict):
        if field_list:
            data = extract_fields(data, field_list)
        if csv_format:
            return to_csv([data], field_list)
        return to_json(data)

    # Handle list of dicts
    if isinstance(data, list):
        if field_list:
            data = [extract_fields(d, field_list) for d in data]
        if csv_format:
            return to_csv(data, field_list)
        return to_json(data)

    # Fallback to JSON for other types
    return to_json(data)


def write_output(
    data: Any,
    output_file: Optional[str] = None,
    csv_format: bool = False,
    fields: Optional[str] = None,
) -> None:
    """Format and write output to file or stdout.

    Args:
        data: Data to output
        output_file: File path to write to (None for stdout)
        csv_format: If True, output CSV instead of JSON
        fields: Comma-separated list of fields to include
    """
    formatted = format_output(data, csv_format=csv_format, fields=fields)

    if output_file:
        with open(output_file, "w") as f:
            f.write(formatted)
    else:
        print(formatted)
