# -*- coding: utf-8 -*-#


# -------------------------------------------------------------------------------
# Name:         TuShare_Test
# Description:
# Author:       orange
# Date:         2021/11/7
# -------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np
import tushare as ts
from matplotlib import ticker
# from mpl_finance import candlestick_ochl #需要另外安装mpl_finance包
from mplfinance.original_flavor import candlestick_ochl  # 需要另外安装mpl_finance包

"""
pd : 数据处理模块
np : 数学模块
ts : 获取数据模块
plt : 绘图模块
"""
pro = ts.pro_api('d199faaeae0b16cd75bec98a6e99eb1671f088f1ca760977db11066c')
# # 输入你自己的设备的api
# # 这个是动态的~~~，你抄我的也没用~~~~
# df = pro.daily(ts_code='000001.SZ', start_date='20190718', end_date='20210308')
# # df 是一个 DataFrame 对象
# # ts_code 是股票代码
# # start_date 是开始日期
# # end_date 世界树日期
# print(df)

# ###################################################

plt.rcParams['font.sans-serif'] = ['SimHei']   # 用来正常显示中文标签

# 具有足够权限的用户是用pro接口获取数据
pro = ts.pro_api()
code = '600004.SH'
df = pro.daily(ts_code=code, start_date='20191201')
df.shape
# stock_daily = pro.daily(ts_code=code, start_date='20181201')
# stock_daily.to_excel('stock_daily.xlsx')	# 保存为电子表格

# 不具有足够权限使用pro接口获取数据的用户执行下面代码，直接从xlxs文件中获取数据
# df = pd.read_excel('stock_daily.xlsx', dtype={'code': 'str','trade_date': 'str'})
# df.drop(df.columns[0], axis=1,  inplace=True)
# df.shape

df2 = df.query('trade_date >= "20171001"').reset_index() #选取2017年10月1日后的数据
df2 = df2.sort_values(by='trade_date', ascending=True)  # 原始数据按照日期降序排列
df2['dates'] = np.arange(0, len(df2)) # len(df2)指记录数
fig, ax = plt.subplots(figsize=(20, 9))
fig.subplots_adjust(bottom=0.2) # 控制子图
# ##candlestick_ochl()函数的参数
# ax 绘图Axes的实例
# quotes  序列（时间，开盘价，收盘价，最高价，最低价） 时间是float类型，date必须转换为float
# width    图像中红绿矩形的宽度,代表天数
# colorup  收盘价格大于开盘价格时的颜色
# colordown   低于开盘价格时矩形的颜色
# alpha      矩形的颜色的透明度
candlestick_ochl(ax, quotes=df2[['dates', 'open', 'close', 'high', 'low']].values,
                 width=0.55, colorup='r', colordown='g', alpha=0.95)
date_tickers = df2['trade_date'].values


def format_date(x, pos):
    if (x < 0) or (x > len(date_tickers)-1):
        return ''
    return date_tickers[int(x)]

ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))  # 按一定规则选取并在水平轴上显示时间刻度
plt.xticks(rotation=30)  # 设置日期刻度旋转的角度
ax.set_ylabel('交易价格')
plt.title(code)
plt.grid(True)  # 添加网格，可有可无，只是让图像好看一些
plt.xlabel('交易日期')
plt.show()