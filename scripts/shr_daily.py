#########################################################################
# File Name: albedo_daily.py
# Author: LIKE NING @ Tsinghua Univ.
# mail: ning.science@gmail.com
# Created Time: Fri 17 Jan 2025 01:07:58 PM CST
#########################################################################
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
# warnings
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import salem
import xarray as xr

data_dir = '/home/ninglk/Chooyu/albedo/data'
# 读取albedo数据
ds = xr.open_mfdataset(os.path.join(data_dir,'shr_2001-2020_daily.nc'))
# 重置时间index
start_date = '2001-01-01'
end_date = '2020-12-31'
time_index = pd.date_range(start=start_date, end=end_date, freq='D')
ds['time']=time_index
ds.to_netcdf(os.path.join(data_dir,'shr_2001-2020_daily_new.nc'))
