#########################################################################
# File Name: albedo_remove_water.py
# Author: LIKE NING @ Tsinghua Univ.
# mail: ning.science@gmail.com
# Created Time: Thu 05 Jun 2025 06:19:37 PM CST
#########################################################################
#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import salem
import geopandas as gpd
import xarray as xr

datadir = "/home/ninglk/Chooyu/1_albedo/2Apr25"
# 修改为包含多个NetCDF文件的文件夹路径
input_folder = os.path.join(datadir, 'albedo_yr') 
shpfile = os.path.join(datadir, 'shpfiles', 'tibet_with_water.shp')

# 确保输出文件夹存在
output_folder = os.path.join(datadir, 'albedo_yr_without_water')
os.makedirs(output_folder, exist_ok=True)

# 检查输入文件夹是否存在
if not os.path.exists(input_folder):
    raise FileNotFoundError(f"输入文件夹不存在: {input_folder}")

# 获取所有NetCDF文件 (支持.nc和.nc4扩展名)
nc_files = [f for f in os.listdir(input_folder) 
            if f.endswith('.nc') or f.endswith('.nc4')]

if not nc_files:
    raise FileNotFoundError(f"在 {input_folder} 中未找到NetCDF文件")

# 循环处理每个文件
for nc_file in nc_files:
    try:
        print(f"处理文件: {nc_file}")
        file_path = os.path.join(input_folder, nc_file)
        
        # 读取数据
        ds = xr.open_dataset(file_path)
        
        # 使用salem进行裁剪
        clipped = ds.Band1.salem.roi(shape=shpfile)
        
        # 构建输出路径
        out_filename = nc_file.replace('.nc', '_without_water.nc')  # 替换原扩展名
        out_path = os.path.join(output_folder, out_filename)
        
        # 保存结果
        clipped.to_netcdf(out_path)
        print(f"✓ 成功保存裁剪文件: {out_path}")
        
        # 显式关闭数据集
        ds.close()
        clipped.close()
    except Exception as e:
        print(f"处理文件 {nc_file} 时出错: {str(e)}")

print("="*50)
print(f"处理完成! 共处理 {len(nc_files)} 个文件, 结果保存在 {output_folder}")
