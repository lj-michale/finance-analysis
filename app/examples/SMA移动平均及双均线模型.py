# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         SMA移动平均及双均线模型
# Description:
# Author:       orange
# Date:         2021/7/13
# -------------------------------------------------------------------------------
import numpy as np
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
import seaborn
import matplotlib as mpl
import warnings

warnings.simplefilter('ignore')   # 忽略警告信息；
mpl.rcParams['font.family'] = 'serif'   # 解决一些字体显示乱码问题

# 获取证券交易数据
data = ts.get_k_data('600030', start='2010-01-01', end='2021-06-30')
# print(data.head())    # DataFrame数据结构
data.set_index('date', inplace=True)   # 设置索引；替换，真实覆盖；

data['SMA_20'] = data['close'].rolling(20).mean()
data['SMA_60'] = data['close'].rolling(60).mean()
data.tail()
print(data.columns.values)
# ['open' 'close' 'high' 'low' 'volume' 'code' 'SMA_20' 'SMA_60']
data[['close', 'SMA_20', 'SMA_60']].plot(figsize=(10, 6))   # 可视化
plt.show()

# 计算股票return
data['returns'] = np.log(data['close'] / data['close'].shift(1))
data['returns_dis'] = data['close']/data['close'].shift(1)-1
data['return_dis2'] = data['close'].pct_change()
data['position'] = np.where(data['SMA_20'] > data['SMA_60'], 1, -1)
data['returns'].cumsum().apply(np.exp).plot(figsize=(10, 6))
# 可视化；计算累计收益，连续下的算法
plt.show()

# ######## SMA策略
data = ts.get_k_data('hs300', start='2010-01-01', end='2021-06-30')
data = pd.DataFrame(data)             # 把data转换成为DataFrame格式
data.rename(columns={'close': 'price'}, inplace=True)      # dict
data.info()
data.set_index('date', inplace=True)        # 覆盖操作
# data.set_index('date')                        # 视图
data['SMA_10'] = data['price'].rolling(10).mean()
data['SMA_60'] = data['price'].rolling(60).mean()
data.tail()
data[['price', 'SMA_10', 'SMA_60']].plot(title='HS300 stock price | 10 & 60 days SMAs',
                                         figsize=(10, 6))
plt.show()

# 策略开发
data['position'] = np.where(data['SMA_10'] > data['SMA_60'], 1, -1)
data.dropna(inplace=True)     # 去掉空值，NaN
data['position'].plot(ylim=[-1.1, 1.1], title='Market Positioning')
plt.show()

# 计算策略年化收益并可视化
data['returns'] = np.log(data['price'] / data['price'].shift(1))
# Numpy向量化；循环做法（尽量避免）,连续return
# data['returns_dis'] = data['price']/data['price'].shift(1)-1    #离散计算return方法1
# data['return_dis2'] = data['price'].pct_change()                #离散计算return方法2
data['returns'].hist(bins=35)
plt.show()

data['strategy'] = data['position'].shift(1) * data['returns']
# 注意未来函数；一般会使得回测收益高估；
data[['returns', 'strategy']].sum()
data[['returns', 'strategy']].cumsum().apply(np.exp).plot(figsize=(10, 6))   # 可视化；离散的计算方法参考Momoentum策略
plt.show()

# 策略收益风险评估
data[['returns', 'strategy']].mean() * 252     # 年化收益率
data[['returns', 'strategy']].std() * 252 ** 0.5   # 年化风险
data['cumret'] = data['strategy'].cumsum().apply(np.exp)
data['cummax'] = data['cumret'].cummax()
data.tail()
data[['cumret', 'cummax']].plot(figsize=(10, 6))
plt.show()

drawdown = (data['cummax'] - data['cumret'])
drawdown.max()           # 计算原理：最大回撤

# 策略优化的一种思路
hs300 = ts.get_k_data('hs300', '2010-01-01', '2021-06-30')[['date', 'close']]
# hs300 = pd.DataFrame(hs300)
hs300.rename(columns={'close': 'price'}, inplace=True)
hs300.set_index('date', inplace=True)
hs300['SMA_10'] = hs300['price'].rolling(10).mean()
hs300['SMA_60'] = hs300['price'].rolling(60).mean()
hs300[['price', 'SMA_10', 'SMA_60']].tail()
hs300[['price', 'SMA_10', 'SMA_60']].plot(grid=True, figsize = (10,8))
plt.show()

hs300['10-60'] = hs300['SMA_10'] - hs300['SMA_60']
hs300['10-60'].tail()

SD = 20                     # 阈值
hs300['regime'] = np.where(hs300['10-60'] > SD, 1,0)
hs300['regime'] = np.where(hs300['10-60'] < -SD, -1,hs300['regime'])    # 核心重要
hs300['regime'].value_counts()
hs300.tail(20)

hs300['Market'] = np.log(hs300['price']/hs300['price'].shift(1))
hs300['Strategy'] = hs300['regime'].shift(1) * hs300['Market']
hs300[['Market','Strategy']].cumsum().apply(np.exp).plot(grid=True, figsize=(10,8))
plt.show()





