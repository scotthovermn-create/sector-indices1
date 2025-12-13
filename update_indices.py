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
        "tickers": ["NEM", "AEM", "B", "KGC", "AU", "SSRM", "FNV", "WPM", "RGLD", "AGI"],  # GOLD → ABX
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
        "color": "#001f3f"
    },
    "Foreign Nat Resources + GGB": {
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
    
    
    all_data[name] = {str(k): v for k, v in index_series.to_dict().items()}

    
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
    title_text="<b>2025 Sector Indices Dashboard</b><br><sup>Equal-weighted • Normalized to 100 one year ago • Updated daily</sup>",
    showlegend=False,
    template="plotly_dark",
 #   template="seaborn",
 #)

# Create sorted performance summary text (centered at bottom)
# performance_summary_sorted = sorted(performance_summary, 
#                                   key=lambda x: float(x["1Y Return"][:-1]), 
#                                   reverse=True)

#summary_lines = ["<b>1-Year Performance Summary (Best to Worst)</b>"]
#for item in performance_summary_sorted:
#    summary_lines.append(f"{item['Sector']:30} {item['1Y Return']:>10}  →  {item['Final Value']}")

#summary_text = "<br>".join(summary_lines)

#fig.update_layout(
#    height=300 + (valid_row * 250),  # Original compact height - fits on one screen
#    title_text="<b>2025 Sector Indices Dashboard</b><br><sup>Equal-weighted • Normalized to 100 one year ago • Updated daily</sup>",
#    showlegend=False,
#    template="plotly_dark",
    margin=dict(l=150, r=150, t=85, b=165)  # Enough bottom space for summary, no excess scrolling
)

# --- 1-Year Summary (already exists) ---
performance_summary_sorted = sorted(performance_summary, 
                                   key=lambda x: float(x["1Y Return"][:-1]), 
                                   reverse=True)

year_lines = ["<b>1-Year Performance (Best at Top)</b>"]
for item in performance_summary_sorted:
    year_lines.append(f"{item['Sector']:30} {item['1Y Return']:>10}  →  {item['Final Value']}")

year_text = "<br>".join(year_lines)

# --- New: 1-Week Summary ---
week_summary = []
for name, info in indices.items():
    if name not in all_data or len(all_data[name]) < 5:  # Need at least ~5 trading days
        continue
    series_dict = all_data[name]
    dates = sorted(series_dict.keys())
    if len(dates) < 5:
        continue
    # Get most recent and ~1 week ago (approx 5 trading days back)
    recent_val = series_dict[dates[-1]]
    week_ago_val = series_dict[dates[-6]]  # -6 to get ~5 days earlier
    week_return = (recent_val / week_ago_val - 1) * 100
    week_summary.append({
        "Sector": name,
        "1W Return": f"{week_return:+.2f}%"
    })

# Sort 1-week by performance
week_summary_sorted = sorted(week_summary, 
                            key=lambda x: float(x["1W Return"][:-1]), 
                            reverse=True)

week_lines = ["<b>1-Week Performance (Best at Top)</b>"]
for item in week_summary_sorted:
    week_lines.append(f"{item['Sector']:30} {item['1W Return']:>10}")

week_text = "<br>".join(week_lines)

# Add summary as annotation WITHOUT overwriting subplot titles

fig.add_annotation(
    text=year_text,
    xref="paper", yref="paper",
    x=0.25, y=-0.33,  # Raised from -0.12 to -0.08
    showarrow=False,
    font=dict(size=11, color="white"),
    align="left",
    bgcolor="rgba(0,0,0,0.7)",
    bordercolor="rgba(0,0,0,0.7)",
    borderwidth=1,
    borderpad=12
)

fig.add_annotation(
    text=week_text,
    xref="paper", yref="paper",
    x=0.75, y=-0.33,  # Same higher position
    showarrow=False,
    font=dict(size=11, color="white"),
    align="left",
    bgcolor="rgba(0,0,0,0.7)",
    bordercolor="rgba(0,0,0,0.7)",
    borderwidth=1,
    borderpad=12
)

# Remove the old single annotation and replace with two side-by-side
 
           

# Save files
fig.write_html("docs/index.html", include_plotlyjs=True)
#fig.write_html("docs/index.html", include_plotlyjs="cdn")

with open("docs/data.json", "w") as f:
    import json
    json.dump(all_data, f, indent=2, default=str)

# Summary
print("\n=== 1-YEAR PERFORMANCE SUMMARY ===")
for item in sorted(performance_summary, key=lambda x: float(x["1Y Return"][:-1]), reverse=True):
    print(f"{item['Sector']}: {item['1Y Return']} → {item['Final Value']}")

print("\nDashboard live at: https://scotthovermn-create.github.io/sector-indices/")
