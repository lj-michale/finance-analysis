# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         基于谷歌搜索的大数据舆情分析策略
# Description:
# Author:       orange
# Date:         2021/7/13
# -------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import quandl
import warnings

# 忽略可能会出现的警告信息，警告并不是错误，可以忽略；
from app.log.LoggingUtil import Logger

warnings.simplefilter('ignore')

logger_path = "E:\\OpenSource\\GitHub\\finance-analysis\\log\\logger.log"
logger = Logger(__name__, logger_path).Logger

"""
1. 策略思想
1.如果当周的谷歌Debt搜索量 > 过去三周平均，则做空道琼斯指数，持仓一周；
2.如果当周的谷歌Debt搜索量 < 过去三周平均，则做多道琼斯指数，持仓一周；
"""

# ################################# 数据整理 ######################################################

# 读取论文数据
paper = pd.read_csv('file:///E:\\OpenSource\\GitHub\\finance-analysis\\dataset\\paper_data.csv',
                    sep=' ',
                    parse_dates=True)
print(paper.columns.values)
"""
['Google Start Date' 'Google End Date' 'arts' 'banking' 'bonds' 'bubble'
 'buy' 'cancer' 'car' 'cash' 'chance' 'color' 'conflict' 'consume'
 'consumption' 'crash' 'credit' 'crisis' 'culture' 'debt' 'default'
 'derivatives' 'dividend' 'dow jones' 'earnings' 'economics' 'economy'
 'energy' 'environment' 'fed' 'finance' 'financial markets' 'fine' 'fond'
 'food' 'forex' 'freedom' 'fun' 'gain' 'gains' 'garden' 'gold' 'greed'
 'growth' 'happy' 'headlines' 'health' 'hedge' 'holiday' 'home' 'house'
 'housing' 'inflation' 'invest' 'investment' 'kitchen' 'labor' 'leverage'
 'lifestyle' 'loss' 'markets' 'marriage' 'metals' 'money' 'movie' 'nasdaq'
 'nyse' 'office' 'oil' 'opportunity' 'ore' 'politics' 'portfolio'
 'present' 'profit' 'rare earths' 'religion' 'restaurant' 'return'
 'returns' 'revenue' 'rich' 'ring' 'risk' 'sell' 'short sell'
 'short selling' 'society' 'stock market' 'stocks' 'success' 'tourism'
 'trader' 'train' 'transaction' 'travel' 'unemployment' 'war' 'water'
 'world' 'DJIA Date' 'DJIA Closing Price']
"""
# print(paper.shape)
# print(paper.head(1))

data = pd.DataFrame({'Google_week': paper['Google End Date'],
                     'Debt': paper['debt'].astype(np.float64),
                     'Date': paper['DJIA Date'],
                     'DJClose': paper['DJIA Closing Price'].astype(np.float64)})
print(data.columns.values)
# ['Google_week' 'Debt' 'Date' 'DJClose']
# 转换为时间序列数据格式才能进行后续的合并等操作；
data['Date'] = pd.to_datetime(data['Date'])
data['Google_week'] = pd.to_datetime(data['Google_week'])

# 2.2 读取我们自己下载的谷歌搜索指数数据
# 注意：论文数据作者有自己做过处理，Normalize，虽然和我们自己下载的数据有非常高的相关性，但是仍然有差别；
trends_download = pd.read_csv("file:///E:\\OpenSource\\GitHub\\finance-analysis\\dataset\\debt_google_trend.csv")
print(trends_download.columns.values)

trends_download['Week'] = trends_download['Week'].apply(lambda x: pd.to_datetime(x.split(' ')[-1]))
print(trends_download.head())

logger.info("进行读取的论文数据与我们自己下载的谷歌搜索指数数据进行整合")
all_data = pd.merge(data,
                    trends_download,
                    left_on='Google_week',
                    right_on='Week')
print(all_data.columns.values)
# print(all_data.head(10))
all_data.drop('Week', inplace=True, axis=1)
all_data.set_index('Date', inplace=True)
all_data.rename(columns={'Debt': 'Debt_paper', 'debt': 'Debt_download'},inplace=True)
both_trends = all_data[['Google_week', 'Debt_paper', 'Debt_download']].set_index('Google_week')
# both_trends.head()
# 数据是经过normalized的，跟我们再google trend数据库里面下载的数据是几乎一致的；
both_trends.corr()
all_data = all_data.reset_index().set_index('Google_week')
all_data['MA_p'] = all_data['Debt_paper'].shift(1).rolling(window=3).mean()
all_data['MA_d'] = all_data['Debt_download'].shift(1).rolling(window=3).mean()

# 产生策略的交易信号
all_data['signal_p'] = np.where(all_data['Debt_paper'] > all_data['MA_p'], -1, 1)
all_data['signal_d'] = np.where(all_data['Debt_download'] > all_data['MA_d'], -1, 1)
all_data.loc[:3, ['signal_p', 'signal_d']] = 0

# 计算策略收益并可视化
all_data['pct_change'] = all_data['DJClose'].pct_change()
all_data['ret_p'] = all_data['pct_change'] * all_data['signal_p'].shift(1)
all_data['ret_d'] = all_data['pct_change'] * all_data['signal_d'].shift(1)

# 计算累积收益；
logger.info("计算累积收益")
all_data['cumret_p'] = (1 + all_data.ret_p).cumprod()
all_data['cumret_d'] = (1 + all_data.ret_d).cumprod()
all_data[['cumret_p', 'cumret_d']].tail(10)
# ['Date' 'Debt_paper' 'DJClose' 'Debt_download' 'MA_p' 'MA_d' 'signal_p' 'signal_d' 'pct_change' 'ret_p' 'ret_d'
# 'cumret_p' 'cumret_d']
logger.info("基于谷歌搜索的大数据舆情分析策略累积收益图形绘制")
plt.figure(figsize=(12, 6))
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.plot(all_data[['Date']], all_data[['cumret_p']], label='cumret_p')
plt.plot(all_data[['Date']], all_data[['cumret_d']], label='cumret_d')
plt.xlabel('year')
plt.title('基于谷歌搜索的大数据舆情分析策略累积收益')
plt.legend(loc='best')
plt.show()

