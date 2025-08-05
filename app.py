



import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="📈 Stock Screener", layout="wide")

st.title("📊 Smart Stock Screener")
st.markdown("Analyze Nifty 50 or custom stocks by **PE Ratio**, **ROE**, **PEG**, and more!")

# Stock input
default_stocks = ["TCS.NS", "INFY.NS", "WIPRO.NS", "HDFCBANK.NS", "RELIANCE.NS"]
tickers = st.text_area("Enter comma-separated stock tickers (or leave blank for Nifty 50)", value=", ".join(default_stocks))
tickers = [x.strip().upper() for x in tickers.split(",") if x.strip()]

# Strategy Selector
strategy = st.selectbox(
    "📊 Choose a Screening Strategy",
    [
        "High ROE and Low PE (Plan 1)",
        "PE < Sector Median (Plan 2)",
        "PEG < 1 and ROE > 15% (exclude negative PEG)"
    ]
)

# Filters
st.sidebar.header("🔍 Filter Criteria")
min_roe = st.sidebar.slider("Minimum ROE (%)", 0.0, 50.0, 15.0)
max_pe = st.sidebar.slider("Maximum PE Ratio", 0.0, 100.0, 25.0)
min_market_cap = st.sidebar.slider("Minimum Market Cap (in ₹ Cr)", 0, 500000, 5000)

@st.cache_data
def get_stock_data(tickers):
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            pe = info.get("trailingPE")
            roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else None
            growth = info.get("earningsQuarterlyGrowth")
            market_cap = info.get("marketCap")

            # Calculate PEG
            if pe and growth and growth > 0:
                peg = round(pe / (growth * 100), 2)
            else:
                peg = None

            data.append({
                'Ticker': ticker,
                'Company': info.get("shortName", ""),
                'Sector': info.get("sector", "N/A"),
                'PE': pe,
                'ROE': roe,
                'PEG': peg,
                'Market Cap': market_cap,
            })
        except Exception as e:
            st.warning(f"Error loading {ticker}: {e}")
    return pd.DataFrame(data)

# Process and filter
if tickers:
    df = get_stock_data(tickers).dropna(subset=["PE", "ROE", "Market Cap"])
    df["Market Cap (₹ Cr)"] = df["Market Cap"] / 1e7  # convert from ₹ to ₹ Crores

    # Apply common pre-filter
    df = df[df["Market Cap (₹ Cr)"] >= min_market_cap]

    # Apply strategy-specific filters
    if strategy == "High ROE and Low PE (Plan 1)":
        df_filtered = df[(df["PE"] <= max_pe) & (df["ROE"] >= min_roe)]
    elif strategy == "PE < Sector Median (Plan 2)":
        df_filtered = pd.DataFrame()
        for sector in df["Sector"].dropna().unique():
            sector_df = df[df["Sector"] == sector]
            sector_median_pe = sector_df["PE"].median()
            selected = sector_df[sector_df["PE"] < sector_median_pe]
            df_filtered = pd.concat([df_filtered, selected])
        df_filtered = df_filtered[df_filtered["ROE"] >= min_roe]
    elif strategy == "PEG < 1 and ROE > 15% (exclude negative PEG)":
        df_filtered = df.dropna(subset=["PEG"])
        df_filtered = df_filtered[(df_filtered["PEG"] > 0) & (df_filtered["PEG"] < 1) & (df_filtered["ROE"] > 15)]

    # Display
    st.subheader("📄 Filtered Stocks")
    st.dataframe(df_filtered.sort_values(by="ROE", ascending=False), use_container_width=True)

    st.subheader("📂 Sector-wise Best Picks")
    for sector in df_filtered["Sector"].unique():
        sector_df = df_filtered[df_filtered["Sector"] == sector]
        if not sector_df.empty:
            best = sector_df.sort_values(by="ROE", ascending=False).iloc[0]
            st.markdown(
                f"**{sector}** → 🏆 {best['Company']} | PE: {round(best['PE'],2)} | ROE: {round(best['ROE'],2)}% | PEG: {best['PEG']} | MCap: ₹{round(best['Market Cap (₹ Cr)'], 2)} Cr"
            )
