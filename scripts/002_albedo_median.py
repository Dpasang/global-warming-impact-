#########################################################################
# File Name: 002_albedo_media.py
# Author: LIKE NING @ Tsinghua Univ.
# mail: ning.science@gmail.com
# Created Time: Thu 05 Jun 2025 11:29:12 PM CST
#########################################################################
#!/usr/bin/env python
# -*- coding:utf-8 -*-

import xarray as xr
import numpy as np
import pandas as pd

# 读取原始数据（包含2020年的逐日反照率）
ds = xr.open_dataset('/home/ninglk/Chooyu/1_albedo/2Apr25/albedo_yr_without_water/albedo_daily_median_2001-2019.nc')
albedo_2020 = ds['albedo_median']  # 假设变量名为'albedo'

# 生成2001-2020年的完整日期范围
dates = pd.date_range('2001-01-01', '2020-12-31')

# 创建空白数据数组（时间×纬度×经度）
new_albedo = xr.DataArray(
    dims=('time', 'lat', 'lon'),
    coords={
        'time': dates,
        'lat': albedo_2020.lat,
        'lon': albedo_2020.lon
    },
    name='albedo'
)

# 提取2020年的月-日索引
month_day_index = albedo_2020['time'].dt.strftime('%m-%d')

# 逐日填充2001-2020年序列
for date in dates:
    # 计算当前日期的月-日
    md = date.strftime('%m-%d')
    
    try:
        # 从2020年找到相同月-日的数据
        source_data = albedo_2020.sel(time=month_day_index == md)
        new_albedo.loc[dict(time=date)] = source_data.values[0]
    except IndexError:
        # 处理闰年的2月29日
        if (date.month == 2) and (date.day == 29):
            # 用2月28日或3月1日替代（这里使用2月28日）
            replacement = albedo_2020.sel(time=month_day_index == '02-28').values[0]
            new_albedo.loc[dict(time=date)] = replacement

# 创建新的数据集并保存
new_ds = xr.Dataset({'albedo': new_albedo})
new_ds.to_netcdf('/home/ninglk/Chooyu/1_albedo/2Apr25/albedo_yr_without_water/albedo_climatology_2001-2019.nc')