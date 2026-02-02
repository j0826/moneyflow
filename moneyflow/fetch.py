"""Fetch quarterly financial data from Yahoo Finance."""

import yfinance as yf
import pandas as pd


def fetch_quarterly_financials(ticker: str) -> dict[str, pd.DataFrame]:
    """Fetch all available quarterly financial statements for a given ticker.

    Returns a dict with keys:
      - income_stmt: Quarterly income statement
      - balance_sheet: Quarterly balance sheet
      - cashflow: Quarterly cash flow statement
    """
    stock = yf.Ticker(ticker)

    data = {
        "income_stmt": stock.quarterly_income_stmt,
        "balance_sheet": stock.quarterly_balance_sheet,
        "cashflow": stock.quarterly_cashflow,
    }

    # Transpose so rows=quarters, columns=metrics; sort by date ascending
    for key in data:
        df = data[key]
        if df is not None and not df.empty:
            df = df.T.sort_index()
            df.index.name = "Quarter"
            data[key] = df
        else:
            data[key] = pd.DataFrame()

    return data


def get_key_metrics(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Extract a curated set of key metrics across statements into one DataFrame.

    Rows = quarters, columns = selected metrics.
    Silently skips any metric not present in the data.
    """
    picks = {
        "income_stmt": [
            "Total Revenue",
            "Net Income",
            "Gross Profit",
            "Operating Income",
            "EBITDA",
            "Basic EPS",
        ],
        "balance_sheet": [
            "Total Assets",
            "Total Liabilities Net Minority Interest",
            "Stockholders Equity",
            "Cash And Cash Equivalents",
            "Total Debt",
        ],
        "cashflow": [
            "Operating Cash Flow",
            "Free Cash Flow",
            "Capital Expenditure",
        ],
    }

    frames = []
    for sheet, cols in picks.items():
        df = data.get(sheet)
        if df is None or df.empty:
            continue
        available = [c for c in cols if c in df.columns]
        if available:
            frames.append(df[available])

    if not frames:
        return pd.DataFrame()

    merged = pd.concat(frames, axis=1)
    merged.index.name = "Quarter"
    return merged
