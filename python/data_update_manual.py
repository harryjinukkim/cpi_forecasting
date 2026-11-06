#!/usr/bin/env python3
"""Download six U.S. macroeconomic series from FRED as CSV files.

The API key is read from ``FRED_API_KEY`` in a ``.env`` file located beside
this script. An already-defined operating-system environment variable takes
precedence over the value in the file.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import ssl
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


@dataclass(frozen=True)
class Series:
    series_id: str
    filename: str
    indicator: str
    unit: str


SERIES = (
    Series("UNRATE", "unemployment_rate.csv", "Unemployment rate", "Percent"),
    Series("CPIAUCSL", "cpi.csv", "Consumer Price Index", "Index 1982-1984=100"),
    Series("FEDFUNDS", "federal_funds_rate.csv", "Federal funds effective rate", "Percent"),
    Series("DCOILWTICO", "oil_prices_wti.csv", "WTI crude oil price", "U.S. dollars per barrel"),
    Series("M2SL", "m2_money_supply.csv", "M2 money supply", "Billions of U.S. dollars"),
    Series("GDPC1", "real_gdp.csv", "Real Gross Domestic Product", "Billions of chained 2017 dollars"),
)


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE entries without overwriting existing variables."""
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def create_ssl_context() -> ssl.SSLContext:
    """Create a verified TLS context, using certifi when it is available."""
    try:
        import certifi
    except ModuleNotFoundError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def fetch_observations(series: Series, api_key: str, timeout: int) -> list[dict[str, str]]:
    """Fetch every available observation for one FRED series."""
    query = urlencode(
        {
            "series_id": series.series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "asc",
            "limit": 100000,
        }
    )
    request = Request(f"{FRED_URL}?{query}", headers={"User-Agent": "fred-macro-manual/1.0"})

    try:
        with urlopen(request, timeout=timeout, context=create_ssl_context()) as response:
            payload = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(detail).get("error_message", detail)
        except json.JSONDecodeError:
            message = detail
        raise RuntimeError(f"FRED API error for {series.series_id}: {message}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Network error for {series.series_id}: {exc}") from exc

    rows: list[dict[str, str]] = []
    for item in payload.get("observations", []):
        rows.append(
            {
                "date": item.get("date", ""),
                "value": "" if item.get("value") == "." else item.get("value", ""),
                "series_id": series.series_id,
                "indicator": series.indicator,
                "unit": series.unit,
            }
        )
    if not rows:
        raise RuntimeError(f"FRED returned no observations for {series.series_id}.")
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """Write atomically so a stopped download cannot leave a partial CSV."""
    fields = ["date", "value", "series_id", "indicator", "unit"]
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def download_all(api_key: str, output_root: Path, timeout: int) -> Path:
    """Download each series separately into the output directory."""
    output_root.mkdir(parents=True, exist_ok=True)

    for series in SERIES:
        logging.info("Downloading %s (%s)", series.indicator, series.series_id)
        rows = fetch_observations(series, api_key, timeout)
        write_csv(output_root / series.filename, rows)

    logging.info("Finished. CSV files saved to %s", output_root)
    return output_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Download FRED macro data as CSV files.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "fred_data",
        help="CSV destination (default: fred_data beside this script)",
    )
    parser.add_argument("--timeout", type=int, default=30, help="network timeout in seconds")
    args = parser.parse_args()

    env_path = Path(__file__).resolve().parent / ".env"
    load_env_file(env_path)
    api_key = os.environ.get("FRED_API_KEY", "").strip()
    if not api_key:
        print(
            f"Error: Add FRED_API_KEY to {env_path} or set it as an environment variable. "
            "Get a key at "
            "https://fred.stlouisfed.org/docs/api/api_key.html",
            file=sys.stderr,
        )
        return 2
    if args.timeout <= 0:
        print("Error: --timeout must be greater than zero.", file=sys.stderr)
        return 2

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    output = args.output_dir.expanduser().resolve()
    try:
        download_all(api_key, output, args.timeout)
    except KeyboardInterrupt:
        logging.info("Stopped by user.")
        return 130
    except Exception as exc:
        logging.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
