# -*- coding: utf-8 -*-
"""PairsTrading.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15s8qtxTFsbePDeEqNx9muvn5WFrqvuVw
"""

import pandas as pd
import pandas_datareader as pdr
from datetime import datetime
import yfinance as yf

def get_data(tickers):
  data = pd.DataFrame()
  names = list()
  for i in tickers:
    data = pd.concat([data, pd.DataFrame(yf.download(i, start=datetime(2023, 11, 17), end = datetime(2024, 11, 17)).iloc[:,4])], axis = 1)
    names.append(i)
  data.columns = names
  return data

ticks = ['QQQ', 'NVDA', 'LLY', 'COIN','UNH','ORCL','TXN', 'SPY', 'TSLA', 'PLTR', 'MARA', 'SMCI', 'QCOM', 'PANW', 'GS', 'MSTR', 'META']
df = get_data(ticks)

df.tail()

import seaborn as sn
import matplotlib.pyplot as plt
import seaborn as sns

correlationHeatMap = df.corr()
plt.figure(figsize = (11,6))
sns.heatmap(correlationHeatMap, annot = True, cmap = 'coolwarm')
plt.title('Correlation Heatmap')
plt.show()

from statsmodels.tsa.stattools import adfuller
from itertools import combinations

#Finding cointegrated pairs
stock_pairs = list(combinations(ticks, 2))
for pair in stock_pairs:
    spread = df[pair[0]] - df[pair[1]]
    spread_result = adfuller(spread)
    ratio = df[pair[0]]/df[pair[1]]
    ratio_result = adfuller(ratio)
    if spread_result[1] < 0.05 and ratio_result[1] < 0.05:
        print(f"Pair {pair} is cointegrated")

stock1 = df['UNH']
stock2 = df['PANW']

# adf test for cointegration and stationarity

spread_adf = adfuller(stock1-stock2)
print("p-value for spread (stock1-stock2): ", spread_adf[1]) # must be < 0.05 for spread to be stationary

ratio_adf = adfuller(stock1/stock2)
print("p-value for ratio (stock1/stock2): ", ratio_adf[1]) # must be < 0.05 for ratio to be stationary

plt.figure(figsize=(5, 2), dpi=200)
plt.plot(stock1, label = 'UNH')
plt.plot(stock2, label = 'PANW')
plt.title('Closing Prices')
plt.legend()

plt.figure(figsize = (5,2), dpi = 200)
plt.plot(stock1-stock2, label = 'Spread of UNH and PANW')
plt.legend()
plt.title("UNH and PANW Spread")

plt.figure(figsize=(6, 3), dpi=200)
ratio = stock1/stock2
plt.plot(ratio, label = 'Price Ratio UNH/PANW')
plt.axhline(ratio.mean(), color='black')
plt.legend()
plt.title("Price Ratio between UNH and PANW")

# Massaging the data because the price scales are different for visualization

scaled_stock2 = stock2 * (stock1.mean() / stock2.mean())

plt.figure(figsize=(5, 2), dpi=200)
plt.plot(stock1, label = 'UNH')
plt.plot(scaled_stock2, label = 'PANW (scaled)')
plt.title('Closing Prices')
plt.legend()

# z-score

plt.figure(figsize=(5, 3), dpi=200)

zscore = (ratio - ratio.mean())/ratio.std()
plt.plot(zscore, label = 'Z Scores')
plt.axhline(zscore.mean(), color = 'black')
plt.axhline(1.0, color = 'red')
plt.axhline(1.25, color = 'red')
plt.axhline(-1.0, color = 'green')
plt.axhline(-1.25, color = 'green')
plt.title('z-core for ratios for UNH and PANW')
plt.show()

# Moving Average for Ratio
plt.figure(figsize = (5,3), dpi = 200)
moving_avg_ratio5 = ratio.rolling(window = 5, center = False).mean()
moving_avg_ratio20 = ratio.rolling(window = 20, center = False).mean()
plt.plot(ratio)
plt.plot(moving_avg_ratio5)
plt.plot(moving_avg_ratio20)
plt.legend(['Ratio', '5 Day Moving Avg Ratio', '20 Day Moving Avg Ratio'])
plt.xlabel('Date')
plt.ylabel('Ratio')
plt.show()

# z-score for rolling ratio

std_20 = ratio.rolling(window = 20, center = False).std()
zscore_20_5 = (moving_avg_ratio5-moving_avg_ratio20)/std_20
plt.figure(figsize = (5,3), dpi = 200)
plt.plot(zscore_20_5)
plt.axhline(1, color = 'red')
plt.axhline(1.25, color = 'red')
plt.axhline(-1, color = 'green')
plt.axhline(-1.25, color = 'green')
plt.axhline(0, color = 'black')
plt.legend(['Rolling Ratio z-score', 'Mean', '+1','+1.25','-1','-1.25'])

# Buy and Sell

plt.figure(figsize=(7, 3), dpi=200)
plt.plot(ratio)
buy = ratio.copy()
sell = ratio.copy()
buy[zscore_20_5 > -1] = 0
sell[zscore_20_5 < 1] = 0
plt.plot(buy, color='g', linestyle='None', marker='^')
plt.plot(sell, color='r', linestyle='None', marker='^')
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, ratio.min(), ratio.max()))
plt.legend(['Ratio', 'Buy', 'Sell'])
plt.show()

# Backtesting
