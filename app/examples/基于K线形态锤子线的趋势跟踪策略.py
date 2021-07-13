# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         基于K线形态锤子线的趋势跟踪策略
# Description:
# Author:       orange
# Date:         2021/7/13
# -------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import tushare as ts
import matplotlib
import matplotlib.pyplot as plt
from app.log.LoggingUtil import Logger

logger_path = "E:\\OpenSource\\GitHub\\finance-analysis\\log\\logger.log"
logger = Logger(__name__, logger_path).Logger

"""
1.基本原理
    1.1 K线部位定义：
    实体：某一根K线开盘价和收盘价之间部分;
    上影线：某一根K线最高价到实体上端的部分;
    下影线：某一根K线最低价到实体下端的部分;

    1.2 锤子线定义
    实体处于整个价格区间上端，实体颜色本身不影响;
    下影线长度至少达到实体高度的2倍;
    上影线很短;

    1.3 策略原理
    在下跌过程中，当某一日出现锤子线，意味着当天行情先继续下跌后出现大幅反弹，行情可能由此反转; 由此以观察期均线识别趋势下跌，以下跌趋势中出现锤子线作为开仓信号;
    采用移动止损方式进行止损构建此策略;

    1.4 止损条件
    当天最低价 < max(均价-观察期内一定倍数的标准差，开仓价-开仓时标准差）;

    锤子线
    1.5 形态要点：
    在出现锤头线（锤子线）之前，股价需经过一段时间的下跌后，处于下跌趋势中，此时出现此形态才具有参考意义；
    锤头实体越小，下影线越长，止跌作用就越明显，参考价值越大；
"""
ts.set_token('5f48e84b07f35508e04ba8c8da76e810ca06de2c29b5d1e9cca19f60')
code = '002398'         # 股票代码
body_size = 0.03        # 表示锤子实体大小上限，基准为当日开盘价，实体不能太大，波动范围限制在3%；
head_size = 0.5         # 表示锤子上影线长度上限，基准为下影线长度，上影线要短一点，不能超过下影线的的一半；
tail_size = 2           # 表示下影线与实体大小比值，下影线要大于实体两倍；
length = 10             # 表示观察期时间长短；
stoplose_trigger = 1    # 表示当价格偏离均线满足几倍标准差时止损
# data = ts.get_h_data(code, '2010-01-01', '2019-03-01')
pro = ts.pro_api()
data = pro.daily(ts_code='002398.SZ', start_date='20150101', end_date='20210618')
data.sort_index(ascending=True, inplace=True)
print(data)
#         ts_code trade_date   open  ...  pct_chg       vol       amount
# 0     002398.SZ   20210618   7.30  ...  -1.7931  58004.20   41613.4260
# 1     002398.SZ   20210617   7.00  ...   3.2764  91894.79   66220.9420
# 2     002398.SZ   20210616   7.08  ...  -1.1268  19134.18   13463.1620
# 3     002398.SZ   20210615   7.07  ...   0.7092  37499.65   26398.1900
# 4     002398.SZ   20210611   6.99  ...   1.2931  45292.54   31831.7220
# ...         ...        ...    ...  ...      ...       ...          ...
# 1446  002398.SZ   20150109  15.75  ...  -0.4400  27788.38   44062.6453
# 1447  002398.SZ   20150108  16.18  ...  -2.6600  42587.68   67970.9088
# 1448  002398.SZ   20150107  16.34  ...  -1.8800  34807.99   56423.9617
# 1449  002398.SZ   20150106  16.00  ...   2.2300  80328.11  130551.3851
# 1450  002398.SZ   20150105  15.95  ...   1.1300  23295.28   37235.4085

data.reset_index(inplace=True)        # 把索引设置成为默认；为了后面交易策略逻辑循环更方便一些；
data['pct_change'] = data['close'].pct_change()
data['ma'] = data['close'].rolling(length).mean()
data['std'] = data['close'].rolling(length).std()
data.tail()
# 由于实盘中当天的日线级别参考指标未实现，因此使用昨日参考指标指导当日交易,避免未来函数；
data['yes_ma'] = data['ma'].shift(1)          # 昨天的mean和昨天的std；
data['yes_std'] = data['std'].shift(1)

# 识别锤子形态
# 计算实体，上影线，下影线
data['body'] = abs(data['open'] - data['close'])                   # 计算K线实体
data['head'] = data['high'] - data[['open', 'close']].max(axis=1)       # 计算上影线，按行计算
data['tail'] = data[['open', 'close']].min(axis=1) - data['low']        # 计算下影线

logger.info("判断K线各部分是否符合锤子线要求")
data['body_cond'] = np.where(data['body']/data['open'] < body_size, 1, 0)     # 实体的大小比开盘价要小于3%，K线实体不能太大
data['head_cond'] = np.where(data['tail']==0, False, data['head'] / data['tail'] < head_size)   # 上影线不能比下影线的一半长
# 当尾部长度为0，为防止判断除法报错，两步判断；
# data['head_cond'] = np.where(data['head']/data['tail'] < head_size, 1, 0)   有可能tail = 0
data['tail_cond'] = np.where(data['body'] == 0, True, (data['tail']/data['body']) > tail_size)    # 下影线要比实体的两倍更长才满足条件

logger.info("判断K线形态是否符合锤子线")
data['hammer'] = data[['head_cond', 'body_cond', 'tail_cond']].all(axis=1)      # 同时满足以上三个条件才是锤子K线
data['hammer'].tail()
data[data['hammer']].tail(10)

# 由于实盘中当天的日线级别参考指标未实现，因此应根据昨日是否满足锤子形态要求作为开仓信号
data['yes_hammer'] = data['hammer'].shift(1)

# 编写交易逻辑——循环法
flag = 0  # 持仓记录，1代码有仓位，0代表空仓；
for i in range(2 * length, len(data)):  # 从20天开始计算，因为前期数据无效；
    # 如果已持仓，判断是否止损
    if flag == 1:
        stoplose_price = max(data.loc[i, 'yes_ma'] - stoplose_trigger * data.loc[i, 'yes_std'],
                             long_open_price - long_open_delta)
        # 当天价格低于止损价，则进行止损，一个是移动止损，一个是开仓时候的开仓和开仓价-1倍标准差；
        if data.loc[i, 'low'] < stoplose_price:  # 接下来要做的都是止损的操作；
            flag = 0
            data.loc[i, 'return'] = min(data.loc[i, 'open'], stoplose_price) / data.loc[i - 1, 'close'] - 1
            # 计算清盘当天的收益；取min是因为，如果当天开盘价就小于了止损价，那么我们就要以开盘价就止损；
            # 不然会导致策略收益高估；
            # 收益计算时要除以前一天的收盘价；
            #             data.loc[i, 'return'] = stoplose_price/data.loc[i-1, 'close'] - 1

            data.loc[i, 'trade_mark'] = -10  # 表示当天持仓并进行平仓，记录自己当天交易操作，平仓：-10；
            # 开仓是10；持仓为1，方便查阅；

        # 如果不满足止损条件，则继续持仓
        else:
            data.loc[i, 'return'] = data.loc[i, 'close'] / data.loc[i - 1, 'close'] - 1
            data.loc[i, 'trade_mark'] = 1  # 表示当天持仓

    # 如果未持仓，判断是否进行开仓
    else:
        # 判断是否为下降趋势，平均重心是下降的；锤子线开仓要满足形态和下降趋势；
        if data.loc[i - length, 'yes_ma'] > data.loc[i, 'yes_ma']:
            # 判断是否符合锤子形态
            if data.loc[i, 'yes_hammer']:
                # 更改持仓标记
                flag = 1
                # 记录开仓时开仓价格及标准差:是为了做固定止损；
                long_open_price = data.loc[i, 'open']
                long_open_delta = data.loc[i, 'yes_std']
                # 计算当天收益率
                data.loc[i, 'return'] = data.loc[i, 'close'] / data.loc[i, 'open'] - 1  # 以产生信号之后的第二天开盘价开仓；
                data.loc[i, 'trade_mark'] = 10  # 表示当天开仓
                # 当天开仓之后不进行平仓判断

data.tail(50)

# 计算策略收益率
data['return'].fillna(0, inplace=True)  # 对大循环中未处理的：既没有持仓，也不满足开仓条件的日期进行处理，则让这些天的return都等于0
data['strategy_return'] = (data['return'] + 1).cumprod()
data['stock_return'] = (data['pct_change'] + 1).cumprod()
logger.info("策略收益率绘图")

fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(1, 1, 1)
ax.plot(data.stock_return)
ax.plot(data.strategy_return)
plt.title(code)
plt.legend()
plt.show()

"""
【策略改进和优化思考】
考虑成交量的配合：在锤子线后面的一根K线如果放量的话，交易信号更可信
考虑跟其他形态的结合，例如锤子线后面紧跟着一根大阳线，交易信号更可信
考虑和其他技术指标的结合，配合技术指标一起进行条件选股
"""

