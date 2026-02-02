#!/usr/bin/env python3
"""MoneyFlow — Fetch & visualize quarterly financial data from Yahoo Finance.

Usage:
    python main.py AAPL
    python main.py MSFT GOOGL TSLA
"""

import sys
import os

from moneyflow.fetch import fetch_quarterly_financials, get_key_metrics
from moneyflow.visualize import build_dashboard_html


def run(ticker: str) -> None:
    print(f"[*] Fetching quarterly data for {ticker} …")
    data = fetch_quarterly_financials(ticker)

    metrics = get_key_metrics(data)
    if metrics.empty:
        print(f"[!] No financial data found for {ticker}.")
        return

    quarters = len(metrics)
    cols = len(metrics.columns)
    print(f"    → {quarters} quarters, {cols} metrics")

    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", f"{ticker}_dashboard.html")
    build_dashboard_html(metrics, ticker, out_path)
    print(f"    → Dashboard saved to {out_path}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <TICKER> [TICKER …]")
        sys.exit(1)

    tickers = [t.upper() for t in sys.argv[1:]]
    for ticker in tickers:
        run(ticker)

    print("\nDone.")


if __name__ == "__main__":
    main()
