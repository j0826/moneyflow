"""Visualization helpers — pure data display, no analysis."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _quarter_labels(index: pd.Index) -> list[str]:
    """Convert datetime index to readable quarter labels like '2024-Q2'."""
    labels = []
    for dt in index:
        try:
            ts = pd.Timestamp(dt)
            labels.append(f"{ts.year}-Q{ts.quarter}")
        except Exception:
            labels.append(str(dt))
    return labels


def _format_value(v: float) -> str:
    """Human-readable large numbers."""
    abs_v = abs(v)
    if abs_v >= 1e12:
        return f"{v/1e12:.2f}T"
    if abs_v >= 1e9:
        return f"{v/1e9:.2f}B"
    if abs_v >= 1e6:
        return f"{v/1e6:.1f}M"
    if abs_v >= 1e3:
        return f"{v/1e3:.1f}K"
    return f"{v:.2f}"


# ── Revenue & Profitability ──────────────────────────────────────────

def fig_revenue_profit(metrics: pd.DataFrame, ticker: str) -> go.Figure | None:
    """Bar chart: Revenue, Gross Profit, Operating Income, Net Income."""
    cols = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]
    available = [c for c in cols if c in metrics.columns]
    if not available:
        return None

    labels = _quarter_labels(metrics.index)
    fig = go.Figure()
    for col in available:
        fig.add_trace(go.Bar(
            x=labels, y=metrics[col], name=col,
            text=[_format_value(v) for v in metrics[col]],
            textposition="outside",
        ))
    fig.update_layout(
        title=f"{ticker} — Revenue & Profitability (Quarterly)",
        barmode="group", yaxis_title="USD",
        template="plotly_white", height=500,
    )
    return fig


# ── EPS ──────────────────────────────────────────────────────────────

def fig_eps(metrics: pd.DataFrame, ticker: str) -> go.Figure | None:
    if "Basic EPS" not in metrics.columns:
        return None
    labels = _quarter_labels(metrics.index)
    fig = go.Figure(go.Bar(
        x=labels, y=metrics["Basic EPS"], name="Basic EPS",
        text=[f"{v:.2f}" for v in metrics["Basic EPS"]],
        textposition="outside", marker_color="#636EFA",
    ))
    fig.update_layout(
        title=f"{ticker} — Earnings Per Share (Quarterly)",
        yaxis_title="USD / Share", template="plotly_white", height=400,
    )
    return fig


# ── Balance Sheet Snapshot ───────────────────────────────────────────

def fig_balance_sheet(metrics: pd.DataFrame, ticker: str) -> go.Figure | None:
    cols = ["Total Assets", "Total Liabilities Net Minority Interest", "Stockholders Equity"]
    available = [c for c in cols if c in metrics.columns]
    if not available:
        return None

    labels = _quarter_labels(metrics.index)
    fig = go.Figure()
    for col in available:
        fig.add_trace(go.Bar(
            x=labels, y=metrics[col], name=col.replace("Net Minority Interest", ""),
            text=[_format_value(v) for v in metrics[col]],
            textposition="outside",
        ))
    fig.update_layout(
        title=f"{ticker} — Balance Sheet Overview (Quarterly)",
        barmode="group", yaxis_title="USD",
        template="plotly_white", height=500,
    )
    return fig


# ── Cash & Debt ──────────────────────────────────────────────────────

def fig_cash_debt(metrics: pd.DataFrame, ticker: str) -> go.Figure | None:
    cols = ["Cash And Cash Equivalents", "Total Debt"]
    available = [c for c in cols if c in metrics.columns]
    if not available:
        return None

    labels = _quarter_labels(metrics.index)
    fig = go.Figure()
    for col in available:
        fig.add_trace(go.Bar(
            x=labels, y=metrics[col], name=col,
            text=[_format_value(v) for v in metrics[col]],
            textposition="outside",
        ))
    fig.update_layout(
        title=f"{ticker} — Cash vs Debt (Quarterly)",
        barmode="group", yaxis_title="USD",
        template="plotly_white", height=450,
    )
    return fig


# ── Cash Flow ────────────────────────────────────────────────────────

def fig_cashflow(metrics: pd.DataFrame, ticker: str) -> go.Figure | None:
    cols = ["Operating Cash Flow", "Free Cash Flow", "Capital Expenditure"]
    available = [c for c in cols if c in metrics.columns]
    if not available:
        return None

    labels = _quarter_labels(metrics.index)
    fig = go.Figure()
    for col in available:
        fig.add_trace(go.Bar(
            x=labels, y=metrics[col], name=col,
            text=[_format_value(v) for v in metrics[col]],
            textposition="outside",
        ))
    fig.update_layout(
        title=f"{ticker} — Cash Flow (Quarterly)",
        barmode="group", yaxis_title="USD",
        template="plotly_white", height=500,
    )
    return fig


# ── EBITDA ───────────────────────────────────────────────────────────

def fig_ebitda(metrics: pd.DataFrame, ticker: str) -> go.Figure | None:
    if "EBITDA" not in metrics.columns:
        return None
    labels = _quarter_labels(metrics.index)
    fig = go.Figure(go.Bar(
        x=labels, y=metrics["EBITDA"], name="EBITDA",
        text=[_format_value(v) for v in metrics["EBITDA"]],
        textposition="outside", marker_color="#00CC96",
    ))
    fig.update_layout(
        title=f"{ticker} — EBITDA (Quarterly)",
        yaxis_title="USD", template="plotly_white", height=400,
    )
    return fig


# ── Combined Dashboard ───────────────────────────────────────────────

ALL_CHARTS = [
    fig_revenue_profit,
    fig_eps,
    fig_balance_sheet,
    fig_cash_debt,
    fig_cashflow,
    fig_ebitda,
]


def build_dashboard_html(metrics: pd.DataFrame, ticker: str, out_path: str) -> str:
    """Generate a single self-contained HTML file with all charts."""
    parts = [
        "<html><head><meta charset='utf-8'>",
        f"<title>{ticker} Quarterly Financials</title></head><body>",
        f"<h1 style='font-family:sans-serif;text-align:center'>{ticker} — Quarterly Financial Data Dashboard</h1>",
    ]

    chart_count = 0
    for chart_fn in ALL_CHARTS:
        fig = chart_fn(metrics, ticker)
        if fig is not None:
            parts.append(fig.to_html(full_html=False, include_plotlyjs=(chart_count == 0)))
            chart_count += 1

    if chart_count == 0:
        parts.append("<p>No data available for this ticker.</p>")

    # Append raw data table
    parts.append("<h2 style='font-family:sans-serif;text-align:center'>Raw Quarterly Data</h2>")
    parts.append("<div style='overflow-x:auto;margin:0 2em'>")
    parts.append(metrics.to_html(float_format=lambda x: _format_value(x), border=0,
                                  classes="dataframe",
                                  table_id="raw-data"))
    parts.append("</div>")
    parts.append("<style>")
    parts.append("table.dataframe{border-collapse:collapse;font-family:monospace;font-size:13px;margin:auto}")
    parts.append("table.dataframe th,table.dataframe td{padding:6px 12px;border:1px solid #ddd;text-align:right}")
    parts.append("table.dataframe th{background:#f5f5f5}")
    parts.append("</style>")
    parts.append("</body></html>")

    html = "\n".join(parts)
    with open(out_path, "w") as f:
        f.write(html)
    return out_path
