#########################################################################
# File Name: 003_albedo_rf.py
# Author: LIKE NING @ Tsinghua Univ.
# mail: ning.science@gmail.com
# Created Time: Fri 06 Jun 2025 04:26:17 PM CST
#########################################################################
#!/usr/bin/env python
# -*- coding:utf-8 -*-
  
import xarray as xr
import numpy as np
import os

# 输入文件路径
dir = "/home/ninglk/Chooyu/1_albedo/2Apr25/albedo_yr_without_water"
input_nc = os.path.join(dir, "albedo_anomaly_without_water_2001-2020.nc")
swin_file = os.path.join(dir, "swin_kt.txt")
output_nc = os.path.join(dir, "rf_albedo_without_water_2001-2020.nc")

# 读取 swin_kt.txt 文件
with open(swin_file, 'r') as f:
    swin_data = np.array([float(line.strip()) for line in f.readlines()])

# 确保有 7305 个数据点
if len(swin_data) != 7305:
    raise ValueError(f"swin_kt.txt 应包含 7305 行数据，但只找到 {len(swin_data)} 行")

# 打开 NetCDF 文件
ds = xr.open_dataset(input_nc, chunks={'time': 100})

# 查找 albedo 变量
albedo_var_name = None
for var in ds.data_vars:
    if 'albedo' in var.lower():
        albedo_var_name = var
        break

if not albedo_var_name:
    raise ValueError("在 NetCDF 文件中找不到包含 'albedo' 的变量")

# 检查时间维度
if len(ds['time']) != 7305:
    raise ValueError(f"NetCDF 文件时间维度应为 7305, 实际为 {len(ds['time'])}")

# 创建 DataArray 用于乘法运算
swin_da = xr.DataArray(
    swin_data,
    dims=['time'],
    coords={'time': ds['time']}
)

# 执行乘法运算（自动广播到空间维度）
ds[albedo_var_name] = -1 * ds[albedo_var_name] * swin_da / 1000

# 保存结果到新文件，添加 NetCDF 压缩
compression_settings = {
    albedo_var_name: {
        'zlib': True,  # 启用压缩
        'complevel': 2  # 压缩级别（1-9，数字越大压缩越强）
    }
}

ds.to_netcdf(output_nc, encoding=compression_settings)
print(f"结果已保存到: {output_nc}，并启用了压缩")

# 关闭数据集
ds.close()