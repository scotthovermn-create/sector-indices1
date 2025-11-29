import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# Create docs folder
os.makedirs("docs", exist_ok=True)

# FIXED TICKERS + COLORS
indices = {
    "Gold Miners": {
        "tickers": ["NEM", "AEM", "ABX", "KGC", "AU", "SSRM", "FNV", "WPM", "RGLD", "AGI"],  # GOLD → ABX
        "color": "#FFD700"
    },
    "Crypto Stocks": {
        "tickers": ["MSTR", "STRK", "COIN", "MARA", "RIOT", "ETHE", "IBIT"],
        "color": "#F7931A"
    },
    "AI & Semis": {
        "tickers": ["NVDA", "MU", "GOOG", "AVGO", "TSM", "TSLA"],
        "color": "#76b900"
    },
    "Oil & Gas Small Cap": {
        "tickers": ["NOG", "MUR", "WHD"],
        "color": "#000000"
    },
    "Foreign Nat Resources & Steel": {
        "tickers": ["VALE", "SQM", "GGB", "TTE", "SCCO"],
        "color": "#c41e3a"
    }
}

end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

all_data = {}
performance_summary = []
fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                    subplot_titles=list(indices.keys()))

valid_row = 0  # Only plot sectors that actually have data

for name, info in indices.items():
    print(f"Fetching {name}...")
    data = yf.download(info["tickers"], start=start_date, end=end_date,
                       progress=False, auto_adjust=True)["Close"]  # auto_adjust=True fixes warning
    
    # Clean data
    data = data.ffill().dropna(how='all')  # pandas >=2.1 syntax
    
    if data.empty or len(data) < 2:
        print(f"  → No valid data for {name}, skipping")
        continue
    
    # Equal-weight normalized index
    normalized = data.div(data.iloc[0]) * 100
    index_series = normalized.mean(axis=1)
    
    all_data[name] = index_series.to_dict()
    
    total_return = (index_series.iloc[-1] / 100 - 1) * 100
    performance_summary.append({
        "Sector": name,
        "1Y Return": f"{total_return:+.2f}%",
        "Final Value": f"{index_series.iloc[-1]:.1f}"
    })
    
    # Plot only if we have data
    valid_row += 1
    fig.add_trace(
        go.Scatter(x=index_series.index, y=index_series.values,
                   name=name, line=dict(color=info["color"], width=3)),
        row=valid_row, col=1
    )

# Only set height based on how many actually plotted
fig.update_layout(
    height=300 + (valid_row * 250),
    title_text="<b>2025 Sector Indices Dashboard</b><br><sup>Equal-weighted • Normalized to 100 one year ago • Updated daily</sup>",
    showlegend=False,
    template="plotly_dark"
)

# Save files
fig.write_html("docs/index.html", include_plotlyjs="cdn")

with open("docs/data.json", "w") as f:
    import json
    json.dump(all_data, f, indent=2, default=str)

# Summary
print("\n=== 1-YEAR PERFORMANCE SUMMARY ===")
for item in sorted(performance_summary, key=lambda x: float(x["1Y Return"][:-1]), reverse=True):
    print(f"{item['Sector']}: {item['1Y Return']} → {item['Final Value']}")

print("\nDashboard live at: https://scotthovermn-create.github.io/sector-indices/")
