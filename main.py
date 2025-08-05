import yfinance as yf
import time
from collections import defaultdict
import matplotlib.pyplot as plt

# 🎯 Default Nifty 50 Stocks
nifty_50_tickers = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "KOTAKBANK.NS", "LT.NS", "SBIN.NS", "AXISBANK.NS", "HCLTECH.NS",
    "ITC.NS", "HINDUNILVR.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "TITAN.NS",
    "ULTRACEMCO.NS", "BAJFINANCE.NS", "MARUTI.NS", "NESTLEIND.NS", "WIPRO.NS",
    "SUNPHARMA.NS", "ONGC.NS", "COALINDIA.NS", "TECHM.NS", "POWERGRID.NS",
    "NTPC.NS", "TATAMOTORS.NS", "JSWSTEEL.NS", "ADANIENT.NS", "BAJAJ-AUTO.NS",
    "EICHERMOT.NS", "HEROMOTOCO.NS", "M&M.NS", "HINDALCO.NS", "BPCL.NS",
    "BRITANNIA.NS", "GRASIM.NS", "TATASTEEL.NS", "INDUSINDBK.NS", "DIVISLAB.NS",
    "CIPLA.NS", "BAJAJFINSV.NS", "SBILIFE.NS", "HDFCLIFE.NS", "SHREECEM.NS",
    "DRREDDY.NS", "ADANIPORTS.NS", "TATACONSUM.NS", "UPL.NS", "ICICIPRULI.NS"
]

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
    except Exception as e:
        print(f"❌ Error fetching {ticker}: {e}")
        return None

    return {
        'Ticker': ticker,
        'Name': info.get('shortName'),
        'Price': info.get('currentPrice'),
        'PE Ratio': info.get('trailingPE'),
        'Sector': info.get('sector'),
        'Market Cap': info.get('marketCap'),
        'ROE': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None
    }

# ✍️ User input
user_input = input("Enter tickers (comma-separated) or press enter to use Nifty 50: ").strip()
tickers = [t.strip().upper() for t in user_input.split(',') if t.strip()] if user_input else nifty_50_tickers

filtered_results = []

for ticker in tickers:
    data = get_stock_data(ticker)
    time.sleep(1.5)  # avoid rate-limiting
    if data and all(data[k] for k in ['Price', 'PE Ratio', 'Sector', 'Market Cap']):
        if data['PE Ratio'] < 30 and data['Market Cap'] > 5_000 * 1e7:
            filtered_results.append(data)

# 📊 Sector-wise grouping
sector_groups = defaultdict(list)
for stock in filtered_results:
    sector_groups[stock['Sector']].append(stock)

# 📋 Ask user for filters
print("\n🔧 Apply custom filters:\n")
min_roe = float(input("Minimum ROE % (e.g. 10): ") or 0)
max_pe = float(input("Maximum PE Ratio (e.g. 30): ") or 100)
min_market_cap = float(input("Minimum Market Cap in Cr (e.g. 50000): ") or 0) * 1e7
sector_filter = input("Filter by Sector (optional, e.g. Technology): ").strip().lower()

# 🔍 Filter for visualization
filtered_for_plot = [
    stock for stock in filtered_results
    if stock['ROE'] is not None
    and stock['ROE'] >= min_roe
    and stock['PE Ratio'] <= max_pe
    and stock['Market Cap'] >= min_market_cap
    and (not sector_filter or stock['Sector'].lower() == sector_filter)
]

# 🧠 Analysis
print("\n📊 Sector-wise Insights:\n")
for sector, stocks in sector_groups.items():
    print(f"📂 Sector: {sector}")
    best_value = min(stocks, key=lambda x: x['PE Ratio'])
    print(f"Best Value: {best_value['Name']} | PE: {best_value['PE Ratio']}")

    valid_roe = [s for s in stocks if s['ROE'] is not None]
    if valid_roe:
        growth = max(valid_roe, key=lambda x: x['ROE'])
        print(f"High Growth: {growth['Name']} | ROE: {growth['ROE']}%")
    else:
        print("High Growth: Data not available")

    avg_pe = sum(s['PE Ratio'] for s in stocks) / len(stocks)
    outliers = [s for s in stocks if s['PE Ratio'] > 1.5 * avg_pe]
    if outliers:
        print("⚠️ Outliers (PE too high):")
        for o in outliers:
            print(f"   - {o['Name']} | PE: {o['PE Ratio']}")
    else:
        print("No extreme outliers.")
    print("-" * 50)

# 📈 Plotting
if filtered_for_plot:
    plt.figure(figsize=(12, 7))
    for stock in filtered_for_plot:
        plt.scatter(stock['PE Ratio'], stock['ROE'], label=stock['Name'])

    plt.xlabel("PE Ratio")
    plt.ylabel("ROE (%)")
    plt.title("PE vs ROE (Filtered Stocks)")
    plt.legend(fontsize=7, loc="best")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("\n❌ No stocks match your filters.\n")
