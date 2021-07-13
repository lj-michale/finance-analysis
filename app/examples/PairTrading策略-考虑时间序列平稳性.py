# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         PairTrading策略-考虑时间序列平稳性
# Description:
# Author:       orange
# Date:         2021/7/13
# -------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import tushare as ts
import seaborn
from matplotlib import pyplot as plt

from app.log.LoggingUtil import Logger

stocks_pair = ['600199', '600702']

logger_path = "E:\\OpenSource\\GitHub\\finance-analysis\\log\\logger.log"
logger = Logger(__name__, logger_path).Logger

m = np.array([1, 2, 3, 4, 5])
n = m * 5 + 2
slope, intercept = np.polyfit(m, n , 1).round(2)       # np.polyfit()   unpacked

data1 = ts.get_k_data('600199', '2013-06-01', '2014-12-31')[['date', 'close']]
data2 = ts.get_k_data('600702', '2013-06-01', '2014-12-31')['close']
data = pd.concat([data1, data2], axis=1)
data.set_index('date', inplace=True)
data.columns = stocks_pair
data.iloc[:, 0]                   # index location,通过索引来获得相关数据,.loc .ix

# 数据准备 & 回测准备
data1 = ts.get_k_data('600199', '2013-06-01', '2014-12-31')[['date','close']]
data2 = ts.get_k_data('600702', '2013-06-01', '2014-12-31')['close']
data = pd.concat([data1, data2], axis=1)
data.set_index('date', inplace=True)
data.columns = stocks_pair
data.plot(figsize=(8, 6))
plt.show()

# 策略开发思路
logger.info("策略开发")
plt.figure(figsize=(10, 8))
plt.title('Stock Correlation')
plt.plot(data['600199'], data['600702'], '.')
plt.xlabel('600199')
plt.ylabel('600702')
data.dropna(inplace=True)

[slope, intercept] = np.polyfit(data.iloc[:, 0], data.iloc[:, 1], 1).round(2)
data['spread'] = data.iloc[:, 1] - data.iloc[:, 0]*slope - intercept
# 误差spread=y-4.29-0.97x
# y：199   x:702
data['spread'].plot(figsize=(10, 8), title='Price Spread')
data['zscore'] = (data['spread'] - data['spread'].mean())/data['spread'].std()   # 标准化，  .std()方差
data['zscore'].plot(figsize = (10,8),title = 'Z-score')
plt.axhline(1.5)
plt.axhline(0)
plt.axhline(-1.5)

# 产生交易信号
data['position_1'] = np.where(data['zscore'] > 1.5, 1, np.nan)
data['position_1'] = np.where(data['zscore'] < -1.5, -1, data['position_1'])
data['position_1'] = np.where(abs(data['zscore']) < 0.5, 0, data['position_1'])
data['position_1'] = data['position_1'].fillna(method='ffill')
data['position_1'].plot(ylim=[-1.1, 1.1], figsize=(10, 6), title='Trading Signal_Uptrade')
plt.show()

data['position_2'] = -np.sign(data['position_1'])
data['position_2'].plot(ylim=[-1.1, 1.1], figsize=(10, 6), title='Trading Signal_Downtrade')
plt.show()

# 计算策略年化收益并可视化
data['returns_1'] = np.log(data['600199'] / data['600199'].shift(1))
data['returns_2'] = np.log(data['600702'] / data['600702'].shift(1))
data['strategy'] = 0.5*(data['position_1'].shift(1) * data['returns_1']) \
                   + 0.5*(data['position_2'].shift(1) * data['returns_2'])

data[['returns_1', 'returns_2', 'strategy']].dropna().cumsum().apply(np.exp).plot(figsize=(10, 8), title='Strategy_Backtesting')
plt.show()

"""
【策略的思考】
 1. 对多只ETF进行配对交易，是很多实盘量化基金的交易策略
【策略的风险和问题】
 1. Spread不回归的风险，当市场结构发生重大改变时，用过去历史回归出来的Spread会发生不回归的重大风险
 2. 中国市场做空受到限制，策略中有部分做空的收益是无法获得的
 3. 回归系数需要Rebalancing（系数要改变）
 4. 策略没有考虑交易成本和其他成本
"""











