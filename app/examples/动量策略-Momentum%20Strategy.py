# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         动量策略-Momentum%20Strategy
# Description:
# Author:       orange
# Date:         2021/7/13
# -------------------------------------------------------------------------------
import numpy as np
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings

from app.log.LoggingUtil import Logger

logger_path = "E:\\OpenSource\\GitHub\\finance-analysis\\log\\logger.log"
logger = Logger(__name__, logger_path).Logger

warnings.simplefilter('ignore')       # 忽略警告信息

plt.style.use('seaborn')
mpl.rcParams['font.family'] = 'serif'

np.sign(-0.02)                  # 重要函数
date = '2014-01-20'
type(date)
data = pd.to_datetime('2014-01-20')
type(data)               # 转换成为时间数据

# 数据准备 & 回测准备
data = ts.get_k_data('hs300', start='2010-01-01', end='2017-06-30')[['date', 'close']]
data.rename(columns={'close': 'price'}, inplace=True)
data.set_index('date', inplace = True)

# 策略开发思路
data['returns'] = np.log(data['price'] / data['price'].shift(1))
data['position'] = np.sign(data['returns'])
# 关键语句,np.sign()很多地方用到；向量化
data['strategy'] = data['position'].shift(1) * data['returns']
# 计算Momentum策略收益；避免未来函数

# 策略可视化
data[['returns', 'strategy']].cumsum().apply(np.exp).plot(figsize=(10, 6))    # 计算出策略的最终的累计收益
plt.show()

# 策略优化之思路——参数优化和穷举
data['position_5'] = np.sign(data['returns'].rolling(5).mean())
data['strategy_5'] = data['position_5'].shift(1) * data['returns']
data[['returns', 'strategy_5']].dropna().cumsum().apply(np.exp).plot(figsize=(10, 6))

# 参数寻优——使用离散Return计算方法
data['returns_dis'] = data['price'] / data['price'].shift(1)-1
# data['returns_dis'] = data['price'].pct_change()
data['returns_dis_cum'] = (data['returns_dis']+1).cumprod()
price_plot = ['returns_dis_cum']    # 这是用来绘制图形的一个list
type(price_plot)

for days in [10,20,30,60]:
    # data['position_%d' % days] = np.sign(data['returns'].rolling(days).mean())
    price_plot.append('sty_cumr_%dd' % days)
    data['position_%dd' % days] = np.where(data['returns'].rolling(days).mean()>0,1,-1)
    data['strategy_%dd' % days] = data['position_%dd' % days].shift(1) * data['returns']
    data['sty_cumr_%dd' % days] = (data['strategy_%dd' % days]+1).cumprod()

data[price_plot].dropna().plot(
    title='HS300 Multi Parameters Momuntum Strategy',
    figsize=(10, 6), style=['--', '--', '--', '--', '--'])
plt.show()

# 策略优化思路之—— High Frequency Data用于Momentum策略
hs300_hf = ts.get_k_data('hs300', ktype='5')
hs300_hf.set_index('date', inplace=True)
hs300_hf.index = hs300_hf.index.to_datetime()
hs300_hf.info()            # Datetime时间数据
hs300_hf['2017-07-15':'2017-07-28'].head()
hs300_hf['returns'] = np.log(hs300_hf['close'] / hs300_hf['close'].shift(1))
hs300_hf['position'] = np.sign(hs300_hf['returns'].rolling(10).mean())     # 10个5分钟平均
hs300_hf['strategy'] = hs300_hf['position'].shift(1) * hs300_hf['returns']
hs300_hf[['returns', 'strategy']].dropna().cumsum().apply(np.exp).plot(figsize=(10, 6),
                                                                       style=['--', '--'])
plt.show()







