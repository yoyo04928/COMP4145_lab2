import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from strategy_backend import load_strategy_data, analyze_results


st.set_page_config(page_title="Trading Strategy Dashboard", layout="wide")


def format_pct(value):
    return f"{value:.2f}%"


@st.cache_data
def get_dashboard_data():
    data, trades = load_strategy_data("MSFT")
    summary = analyze_results(trades)
    return data, trades, summary


data, trades, summary = get_dashboard_data()

st.title("MSFT Golden Cross Strategy Dashboard")

chart_tab, stats_tab, trades_tab = st.tabs([
    "Price Chart",
    "Trade Statistics",
    "Detailed Trades",
])

with chart_tab:
    st.subheader("Price, MA50, MA200, Buy and Sell Points")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="Close Price",
        line={"color": "#1f77b4", "width": 2},
    ))
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["MA50"],
        mode="lines",
        name="MA50",
        line={"color": "#ff7f0e", "width": 2},
    ))
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["MA200"],
        mode="lines",
        name="MA200",
        line={"color": "#d62728", "width": 2},
    ))

    if not trades.empty:
        buy_points = trades[["BuyDate", "BuyPrice"]].rename(columns={"BuyDate": "Date", "BuyPrice": "Price"})
        sell_points = trades[["SellDate", "SellPrice"]].rename(columns={"SellDate": "Date", "SellPrice": "Price"})

        fig.add_trace(go.Scatter(
            x=buy_points["Date"],
            y=buy_points["Price"],
            mode="markers",
            name="Buy",
            marker={"size": 10, "color": "#2ca02c", "symbol": "circle"},
        ))
        fig.add_trace(go.Scatter(
            x=sell_points["Date"],
            y=sell_points["Price"],
            mode="markers",
            name="Sell",
            marker={"size": 10, "color": "#d62728", "symbol": "diamond"},
        ))

    fig.update_layout(
        title="MSFT Closing Price with Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=700,
    )
    st.plotly_chart(fig, width="stretch")

with stats_tab:
    st.subheader("Overall Trade Statistics")

    if trades.empty:
        st.warning("No trades were generated from the selected strategy.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Trades", summary["Total Trades"])
        col2.metric("Winning Trades", summary["Winning Trades"])
        col3.metric("Losing Trades", summary["Losing Trades"])
        col4.metric("Win Rate", format_pct(summary["Win Rate"]))

        col5, col6, col7 = st.columns(3)
        col5.metric("Average Profit", format_pct(summary["Average Profit"]))
        col6.metric("Average Holding Days", f"{summary['Average Holding Days']:.1f}")
        col7.metric("Best Trade", format_pct(trades["ProfitPct"].max()))

        profit_chart = trades.set_index("BuyDate")["ProfitPct"].sort_index()
        st.bar_chart(profit_chart)

        st.caption("Profit percentage by trade (buy date as index)")

with trades_tab:
    st.subheader("Detailed Trade Record")

    if trades.empty:
        st.info("No detailed trade data available.")
    else:
        display_df = trades.copy()
        display_df["BuyDate"] = display_df["BuyDate"].dt.strftime("%Y-%m-%d")
        display_df["SellDate"] = display_df["SellDate"].dt.strftime("%Y-%m-%d")
        display_df["BuyPrice"] = display_df["BuyPrice"].round(2)
        display_df["SellPrice"] = display_df["SellPrice"].round(2)
        display_df["ProfitPct"] = display_df["ProfitPct"].round(2)

        st.dataframe(display_df, width="stretch")

        csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download trade data as CSV",
            data=csv,
            file_name="trading_strategy_trades.csv",
            mime="text/csv",
        )
