# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         技术分析策略和交易系统_SMA+CCI交易系统
# Description:
# Author:       orange
# Date:         2021/7/13
# -------------------------------------------------------------------------------

"""
双技术指标：SMA+CCI交易系统
以SMA作为开平仓信号，同时增加CCI作为过滤器；
当股价上穿SMA，同时CCI要小于-100，说明是在超卖的情况下，上穿SMA，做多；交易信号更可信；
当股价下穿SMA，同时CCI要大于+100，说明是在超买的情况下，下穿SMA，做空；交易信号更可信；
"""

import numpy as np
import pandas as pd
import tushare as ts
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
# 确保‘-’号显示正常
mpl.rcParams['axes.unicode_minus']=False
# 确保中文显示正常
mpl.rcParams['font.sans-serif'] = ['SimHei']





