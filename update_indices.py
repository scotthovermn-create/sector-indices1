import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os

# Ensure docs folder exists
os.makedirs("docs", exist_ok=True)

# === 5 SECTOR INDICES ===
indices = {
    "Gold Miners": {
        "tickers": ["NEM", "AEM", "GOLD", "KGC", "AU", "SSRM", "FNV", "WPM", "RGLD", "AGI"],
        "color": "#FFD700"
    },
    "Crypto Stocks": {
        "tickers": ["MSTR", "STRK", "COIN", "MARA", "RIOT", "ETHE", "IBIT"],
        "color": "#F7931A"   # Bitcoin orange
    },
    "AI & Semis": {
        "tickers": ["NVDA", "MU", "GOOG", "AVGO", "TSM", "TSLA"],  # TSM = TSMC
        "color": "#76b900"   # Nvidia green vibe
    },
    "Oil & Gas Small Cap": {
        "tickers": ["NOG", "MUR", "WHD"],
        "color": "#000000"   # Black gold
    },
    "Foreign Nat Resources & Steel": {
        "tickers": ["VALE", "SQM", "GGB", "TTE", "SCCO"],
        "color": "#c41e3a"   # Deep red for emerging markets/steel
    }
}

end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

all_data = {}
performance_summary = []

fig = make_subplots(
    rows=5, cols=1, 
    shared_xaxes=True,
    vertical_spacing=0.05,
    subplot_titles=[name for name in indices.keys()]
)

for row, (name, info) in enumerate(indices.items(), 1):
    print(f"Fetching {name}...")
    data = yf.download(info["tickers"], start=start_date, end=end_date, progress=False)["Adj Close"]
    data = data.fillna(method='ffill').dropna(how='all')
    
    # Equal-weighted normalized index (base = 100)
    normalized = data / data.iloc[0] * 100
    index_series = normalized.mean(axis=1)
    index_series.name = name
    
    all_data[name] = index_series.to_dict()
    
    # Performance stats
    total_return = (index_series.iloc[-1] / 100 - 1) * 100
    performance_summary.append({
        "Sector": name,
        "1Y Return": f"{total_return:+.2f}%",
        "Final Value": f"{index_series.iloc[-1]:.1f}"
    })
    
    # Plot
    fig.add_trace(
        go.Scatter(x=index_series.index, y=index_series.values,
                   name=name, line=dict(color=info["color"], width=3)),
        row=row, col=1
    )

fig.update_layout(
    height=1400,
    title_text="<b>2025 Sector Indices Dashboard</b><br><sup>Equal-weighted, normalized to 100 one year ago — updated daily</sup>",
    showlegend=False,
    template="plotly_dark"
)

# Save HTML
fig.write_html("docs/index.html", include_plotlyjs="cdn")

# Save JSON for anyone who wants raw data
with open("docs/data.json", "w") as f:
    json.dump({k: v for k, v in all_data.items()}, f, indent=2, default=str)

# Print nice summary
print("\n=== 1-YEAR PERFORMANCE SUMMARY ===")
for item in sorted(performance_summary, key=lambda x: float(x["1Y Return"][:-1]), reverse=True):
    print(f"{item['Sector']}: {item['1Y Return']} → {item['Final Value']}")

print("\nDashboard updated → https://YOURUSERNAME.github.io/sector-indices/")
