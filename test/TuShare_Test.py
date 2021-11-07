# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         TuShare_Test
# Description:
# Author:       orange
# Date:         2021/11/7
# -------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
"""
pd : 数据处理模块
np : 数学模块
ts : 获取数据模块
plt : 绘图模块
"""
pro = ts.pro_api('d199faaeae0b16cd75bec98a6e99eb1671f088f1ca760977db11066c')
# 输入你自己的设备的api
# 这个是动态的~~~，你抄我的也没用~~~~
df = pro.daily(ts_code='000001.SZ', start_date='20190718', end_date='20210308')
# df 是一个 DataFrame 对象
# ts_code 是股票代码
# start_date 是开始日期
# end_date 世界树日期
print(df)

