#########################################################################
# FileName: eco_zone_monthly_stats.py
# Author: LIKE NING @ Tsinghua Univ.
# mail: ning.science@gmail.com
# Created Time: Sat 07 Jun 2025 06:55:28 PM CST
#########################################################################
#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import xarray as xr
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import salem
from datetime import datetime

# 1. 设置文件路径
# nc_file = "/home/ninglk/Chooyu/1_albedo/2Apr25/albedo_yr_without_water/gwi_albedo_without_water_2001-2020.nc"
nc_file = "/home/ninglk/Chooyu/1_albedo/2Apr25/albedo_yr_without_water/albedo_anomaly_without_water_2001-2020.nc"

shp_file = "/home/ninglk/Chooyu/1_albedo/2Apr25/shpfiles/Eco-TP.shp"
output_csv = "/home/ninglk/Chooyu/1_albedo/2Apr25/eco_zone_monthly_statistics_albedo_anomaly.csv"

# 2. 读取数据
print("正在读取NetCDF文件...")
ds = xr.open_dataset(nc_file)
albedo = ds['albedo']

print("正在读取生态分区SHP文件...")
eco_zones = gpd.read_file(shp_file)
print(f"找到 {len(eco_zones)} 个生态分区")

# 3. 准备存储所有结果的列表
all_stats = []

# 4. 获取时间信息并转换为年月
times = pd.to_datetime(albedo.time.values)
years = times.year.values
months = times.month.values
unique_years = np.unique(years)
unique_months = np.unique(months)

print(f"数据时间范围: {times[0]} 至 {times[-1]}")
print(f"包含年份: {list(unique_years)}")
print(f"包含月份: {list(unique_months)}")

# 5. 进度条设置
pbar_zones = tqdm(total=len(eco_zones), desc="处理生态分区")

# 6. 为每个生态分区计算逐月统计量
for idx, zone in eco_zones.iterrows():
    zone_name = zone['FID_tibet']  # 根据实际情况调整字段名
    zone_geom = zone['geometry']
    
    # 使用salem进行空间裁剪
    try:
        # 裁剪该分区所有时间段的数据
        zone_data = albedo.salem.roi(geometry=zone_geom)
        
        if zone_data.size == 0:
            print(f"警告: 生态分区 {zone_name} 无有效数据")
            pbar_zones.update(1)
            continue
            
        # 对该分区内每个时间步计算统计量
        for t_idx in range(len(times)):
            # 获取当前时间步数据
            current_data = zone_data.isel(time=t_idx)
            values = current_data.values.flatten()
            values = values[~np.isnan(values)]  # 移除NaN值
            
            if len(values) == 0:
                continue
                
            # 计算统计指标
            stats = {
                'ECO_ID': zone_name,
                'Zone_Name': zone.get('ECO_NAME', ''),  # 根据实际字段调整
                'Year': years[t_idx],
                'Month': months[t_idx],
                'Count': len(values),
                'Mean': float(np.mean(values)),
                'Median': float(np.median(values)),
                'Min': float(np.min(values)),
                'Max': float(np.max(values)),
                'Q1': float(np.percentile(values, 25)),
                'Q3': float(np.percentile(values, 75)),
                'P5': float(np.percentile(values, 5)),
                'P95': float(np.percentile(values, 95)),
                'Std': float(np.std(values))
            }
            all_stats.append(stats)
            
    except Exception as e:
        print(f"处理生态分区 {zone_name} 时出错: {str(e)}")
    
    pbar_zones.update(1)

pbar_zones.close()

# 7. 保存统计结果到CSV
if all_stats:
    stats_df = pd.DataFrame(all_stats)
    
    # 按年份和月份排序
    stats_df = stats_df.sort_values(by=['ECO_ID', 'Year', 'Month'])
    
    # 保存到CSV
    stats_df.to_csv(output_csv, index=False)
    print(f"\n逐月统计结果已保存到: {output_csv}")
    
    # 打印前10行结果
    print("\n统计结果预览:")
    print(stats_df.head(10))
    
    # # 8. 可视化示例：选取第一个分区的时间序列
    # sample_zone = stats_df['ECO_ID'].iloc[0]
    # zone_df = stats_df[stats_df['ECO_ID'] == sample_zone]
    
    # plt.figure(figsize=(12, 8))
    
    # plt.subplot(3, 1, 1)
    # plt.plot(zone_df['Year'] + (zone_df['Month']-1)/12, zone_df['Mean'], 'b-', label='Mean')
    # plt.plot(zone_df['Year'] + (zone_df['Month']-1)/12, zone_df['Median'], 'r-', label='Median')
    # plt.title(f'生态分区 {sample_zone} 反照率均值与中位数时间序列')
    # plt.ylabel('反照率')
    # plt.legend()
    # plt.grid(True)
    
    # plt.subplot(3, 1, 2)
    # plt.plot(zone_df['Year'] + (zone_df['Month']-1)/12, zone_df['Q1'], 'g-', label='Q1 (25%)')
    # plt.plot(zone_df['Year'] + (zone_df['Month']-1)/12, zone_df['Median'], 'r-', label='Median')
    # plt.plot(zone_df['Year'] + (zone_df['Month']-1)/12, zone_df['Q3'], 'b-', label='Q3 (75%)')
    # plt.title(f'四分位距变化')
    # plt.ylabel('反照率')
    # plt.legend()
    # plt.grid(True)
    
    # plt.subplot(3, 1, 3)
    # plt.plot(zone_df['Year'] + (zone_df['Month']-1)/12, zone_df['P5'], 'c-', label='5%分位')
    # plt.plot(zone_df['Year'] + (zone_df['Month']-1)/12, zone_df['P95'], 'm-', label='95%分位')
    # plt.title(f'极端值范围变化')
    # plt.xlabel('时间')
    # plt.ylabel('反照率')
    # plt.legend()
    # plt.grid(True)
    
    # plt.tight_layout()
    # plt.savefig(f'eco_zone_{sample_zone}_ts.png', dpi=300)
    # plt.show()
    # print(f"示例时间序列图已保存为 eco_zone_{sample_zone}_ts.png")
    
else:
    print("错误: 未计算任何分区的统计量")






# #########################################################################
# # File Name: 004_gei_eco.py
# # Author: LIKE NING @ Tsinghua Univ.
# # mail: ning.science@gmail.com
# # Created Time: Sat 07 Jun 2025 06:55:28 PM CST
# #########################################################################
# #!/usr/bin/env python
# # -*- coding:utf-8 -*-

# import os
# import xarray as xr
# import geopandas as gpd
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from tqdm import tqdm

# # 1. 设置文件路径

# nc_file = "/home/ninglk/Chooyu/1_albedo/2Apr25/albedo_yr_without_water/gwi_albedo_without_water_2001-2020.nc"
# shp_file = "/home/ninglk/Chooyu/1_albedo/2Apr25/shpfiles/Eco-TP.shp"
# output_csv = "/home/ninglk/Chooyu/1_albedo/2Apr25/eco_zone_statistics.csv"

# # 2. 读取数据
# print("正在读取NetCDF文件...")
# ds = xr.open_dataset(nc_file)
# gwi = ds['albedo']  # 假设变量名为'gwi'，请根据实际情况调整

# print("正在读取生态分区SHP文件...")
# eco_zones = gpd.read_file(shp_file)
# print(f"找到 {len(eco_zones)} 个生态分区")

# # 3. 准备统计结果存储
# stats_list = []

# # 4. 为每个生态分区计算统计量
# for idx, zone in tqdm(eco_zones.iterrows(), total=len(eco_zones), desc="处理生态分区"):
#     zone_name = zone['FID_tibet']  # 假设分区ID字段为ECO_ID，请根据实际情况调整
#     zone_geom = zone['geometry']
    
#     # 使用salem进行空间裁剪（需要安装salem库）
#     try:
#         import salem
#         # 裁剪数据
#         zone_data = gwi.salem.roi(geometry=zone_geom)
        
#         # 计算统计量
#         values = zone_data.values.flatten()
#         values = values[~np.isnan(values)]  # 移除NaN值
        
#         if len(values) > 0:
#             stats = {
#                 'ECO_ID': zone_name,
#                 'Zone_Name': zone['ECO_NAME'],  # 假设有名称字段
#                 'Count': len(values),
#                 'Mean': np.mean(values),
#                 'Median': np.median(values),
#                 'Q1': np.percentile(values, 25),
#                 'Q3': np.percentile(values, 75),
#                 'P5': np.percentile(values, 5),
#                 'P95': np.percentile(values, 95),
#                 'Min': np.min(values),
#                 'Max': np.max(values),
#                 'Std': np.std(values)
#             }
#             stats_list.append(stats)
#         else:
#             print(f"警告: 生态分区 {zone_name} 无有效数据")
            
#     except ImportError:
#         # 如果没有salem，使用较慢的逐点判断方法
#         from shapely.geometry import Point
        
#         # 获取数据坐标网格
#         lons, lats = np.meshgrid(gwi.lon.values, gwi.lat.values)
#         values = []
        
#         # 遍历每个网格点
#         for i in range(gwi.lat.size):
#             for j in range(gwi.lon.size):
#                 point = Point(lons[i,j], lats[i,j])
#                 if zone_geom.contains(point):
#                     val = gwi.isel(lat=i, lon=j).values
#                     if not np.isnan(val):
#                         values.append(val)
        
#         if len(values) > 0:
#             values = np.array(values)
#             stats = {
#                 'ECO_ID': zone_name,
#                 'Zone_Name': zone['ECO_NAME'],
#                 'Count': len(values),
#                 'Mean': np.mean(values),
#                 'Median': np.median(values),
#                 'Q1': np.percentile(values, 25),
#                 'Q3': np.percentile(values, 75),
#                 'P5': np.percentile(values, 5),
#                 'P95': np.percentile(values, 95),
#                 'Min': np.min(values),
#                 'Max': np.max(values),
#                 'Std': np.std(values)
#             }
#             stats_list.append(stats)
#         else:
#             print(f"警告: 生态分区 {zone_name} 无有效数据")

# # 5. 保存统计结果
# if stats_list:
#     stats_df = pd.DataFrame(stats_list)
#     stats_df.to_csv(output_csv, index=False)
#     print(f"\n统计结果已保存到: {output_csv}")
    
#     # 打印前5行结果
#     print("\n统计结果预览:")
#     print(stats_df.head())
    
#     # 可视化各分区中位数
#     plt.figure(figsize=(12, 6))
#     stats_df.sort_values('Median', ascending=False).plot.bar(x='Zone_Name', y='Median', 
#                                                            legend=False, color='skyblue')
#     plt.title('各生态分区GWI中位数比较', fontsize=14)
#     plt.ylabel('GWI中位数')
#     plt.xticks(rotation=45, ha='right')
#     plt.tight_layout()
#     plt.savefig('eco_zones_median.png', dpi=300)
#     plt.show()
#     print("可视化结果已保存为 eco_zones_median.png")
# else:
#     print("错误: 未计算任何分区的统计量")

# # 6. 空间可视化（可选）
# try:
#     import cartopy.crs as ccrs
#     import cartopy.feature as cfeature
    
#     fig = plt.figure(figsize=(15, 10))
#     ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    
#     # 绘制生态分区
#     eco_zones.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=1, zorder=2)
    
#     # 绘制GWI数据（示例时间点）
#     sample_time = gwi.time[0]
#     gwi.sel(time=sample_time).plot(ax=ax, cmap='viridis', 
#                                  cbar_kwargs={'label': 'GWI'}, zorder=1)
    
#     # 添加地理要素
#     ax.add_feature(cfeature.COASTLINE)
#     ax.add_feature(cfeature.BORDERS, linestyle=':')
#     ax.set_title(f'GWI空间分布与生态分区\n{sample_time.values}', fontsize=14)
    
#     plt.tight_layout()
#     plt.savefig('gwi_eco_zones_map.png', dpi=300)
#     plt.show()
#     print("空间可视化已保存为 gwi_eco_zones_map.png")
    
# except ImportError:
#     print("未安装cartopy，跳过空间可视化")