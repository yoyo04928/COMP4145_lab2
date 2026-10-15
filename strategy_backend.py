import pandas as pd
import yfinance as yf


# Download stock data
def get_stock_data(ticker, period="5y"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data


# Calculate moving averages
def calculate_moving_averages(data):
    data = data.copy()
    data["MA50"] = data["Close"].rolling(window=50).mean()
    data["MA200"] = data["Close"].rolling(window=200).mean()
    return data


# Identify golden cross (buy signal)
def identify_golden_cross(data):
    data = data.copy()
    data["Signal"] = 0
    data["GoldenCross"] = (
        (data["MA50"] > data["MA200"]) &
        (data["MA50"].shift(1) <= data["MA200"].shift(1))
    )
    return data


# Implement trading strategy
def implement_strategy(data):
    positions = []
    working_data = data.iloc[200:].copy()

    buy_dates = working_data[working_data["GoldenCross"] == True].index.tolist()

    for buy_date in buy_dates:
        buy_price = working_data.loc[buy_date, "Close"]
        target_price = buy_price * 1.15
        max_sell_date = buy_date + pd.Timedelta(days=60)
        sell_period = working_data.loc[buy_date:max_sell_date].copy()

        target_reached = sell_period[sell_period["Close"] >= target_price]

        if not target_reached.empty:
            sell_date = target_reached.index[0]
            sell_price = target_reached.loc[sell_date, "Close"]
            sell_reason = "Target reached"
        else:
            sell_date_candidates = sell_period.index.tolist()
            if not sell_date_candidates:
                continue
            sell_date = sell_date_candidates[-1]
            sell_price = working_data.loc[sell_date, "Close"]
            sell_reason = "Max holding period"

        holding_days = (sell_date - buy_date).days
        profit_pct = (sell_price / buy_price - 1) * 100

        positions.append({
            "BuyDate": buy_date,
            "BuyPrice": buy_price,
            "SellDate": sell_date,
            "SellPrice": sell_price,
            "HoldingDays": holding_days,
            "ProfitPct": profit_pct,
            "SellReason": sell_reason,
        })

    return pd.DataFrame(positions)


# Overall analysis
def analyze_results(positions):
    if positions.empty:
        return {
            "Total Trades": 0,
            "Winning Trades": 0,
            "Losing Trades": 0,
            "Win Rate": 0,
            "Average Profit": 0,
            "Average Holding Days": 0,
        }

    total_trades = len(positions)
    win_trades = len(positions[positions["ProfitPct"] > 0])
    loss_trades = total_trades - win_trades
    win_rate = win_trades / total_trades * 100 if total_trades > 0 else 0

    avg_profit = positions["ProfitPct"].mean()
    avg_holding = positions["HoldingDays"].mean()

    return {
        "Total Trades": total_trades,
        "Winning Trades": win_trades,
        "Losing Trades": loss_trades,
        "Win Rate": win_rate,
        "Average Profit": avg_profit,
        "Average Holding Days": avg_holding,
    }


# Load full strategy dataset
def load_strategy_data(ticker="MSFT"):
    data = get_stock_data(ticker)
    data = calculate_moving_averages(data)
    data = identify_golden_cross(data)
    trades = implement_strategy(data)
    return data, trades
