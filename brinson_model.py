import yfinance as yf
import numpy as np
import pandas as pd

# Get all relevant data
_data = {
    'start_date': '2020-01-01',
    'end_date': '2024-12-31',
    'bench_ticker': "^GSPC",  # Benchmark ticker (S&P 500)
    'fund_ticker': "0P0001N8QM.TO",  # Fund ticker (replace with actual fund)
    'tech': "XLK",  # Sector ETF tickers
    'healthcare': "XLV",
    'finance': "XLF",
    'utilities': 'XLU'
}

sector_tickers = [_data['tech'], _data['healthcare'], _data['finance'], _data['utilities']]
fund_ticker = _data['fund_ticker']
bench_ticker = _data['bench_ticker']

# Download sector ETFs and fund data
sector_prices = {sector: yf.download(ticker, start=_data['start_date'], end=_data['end_date'])['Close']
                 for sector, ticker in zip(['Tech', 'Healthcare', 'Finance', 'Utilities'], sector_tickers)}

# Download fund & benchmark data
fund_prices = yf.download(fund_ticker, start=_data['start_date'], end=_data['end_date'])['Close']
bench_prices = yf.download(bench_ticker, start=_data['start_date'], end=_data['end_date'])['Close']

# Calculate sector returns
sector_returns = pd.DataFrame({sector: prices.pct_change().dropna() for sector, prices in sector_prices.items()})

aligned_data = pd.concat([fund_prices, bench_prices, *sector_prices.values()], axis=1, join="inner")
aligned_data.columns = ['Fund', 'Benchmark', 'Tech', 'Healthcare', 'Finance', 'Utilities']

# Calculate the returns for the fund and benchmark
aligned_returns = aligned_data.pct_change().dropna()

# Define weights
fund_weights = np.array([0.25, 0.30, 0.20, 0.25])
benchmark_weights = np.array([0.25, 0.25, 0.25, 0.25])

# Calculate mean sector returns for fund and benchmark
sector_mean_returns = sector_returns.mean()

# Calculate fund sector returns and benchmark sector returns
fund_sector_rets = sector_mean_returns * fund_weights[:len(sector_mean_returns)]
bench_sector_rets = sector_mean_returns * benchmark_weights[:len(sector_mean_returns)]

# Calculate allocation effect
allocation_effect = np.sum((fund_weights - benchmark_weights) * bench_sector_rets)

# Calculate selection effect (note the correction here)
selection_effect = np.sum(benchmark_weights * (fund_sector_rets - bench_sector_rets))

# Calculate interaction effect
interaction_effect = np.sum((fund_weights - benchmark_weights) * (fund_sector_rets - bench_sector_rets))

# Calculate total effect
total_effect = allocation_effect + selection_effect + interaction_effect

# Output results
print(f"Attribution for {fund_ticker} relative to {bench_ticker}:")
print(f"Allocation Effect: {allocation_effect:.6f}")
print(f"Selection Effect: {selection_effect:.6f}")
print(f"Interaction Effect: {interaction_effect:.6f}")
print(f"Total Effect: {total_effect:.6f}")
