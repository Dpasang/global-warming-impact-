#########################################################################
# File Name: 03_excel2sh.py
# Author: LIKE NING @ IGSNRR
# mail: ninglk@igsnrr.ac.cn
# Created Time: Sat Nov 26 09:58:17 2022
#########################################################################
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import glob
import os
from datetime import date

import geopandas as gpd
import numpy as np
import pandas as pd
import salem
import xarray as xr

from scipy.interpolate import griddata



def excel2sh_nearest(filename):
    res = pd.read_excel(filename)
    year = str(filename)[21:25]
    mon = str(filename)[26:28]
    day = str(filename)[29:31]
    outfile = "/mnt/f/albedo_3/sh/sh"+year+mon+day+".nc"
    print(outfile)
    hours = res["hours"].to_numpy()
    lon = res["longitude"].to_numpy()
    lat = res["latitude"].to_numpy()
    data_all = hours.reshape(211, 1)

    grid_lon = np.linspace(75, 105, 1201)
    grid_lat = np.linspace(26, 40, 561)
    lon_target = grid_lon
    lat_target = grid_lat
    x_t, y_t = np.meshgrid(lon_target, lat_target)
    z = griddata((lon, lat), hours, (x_t, y_t), method="nearest")
    dz = xr.Dataset({"hours": (["lat", "lon"], z)}, coords={
                    "lon": ("lon", lon_target),     "lat": ("lat", lat_target), })

    shp_file = "/mnt/qnap/tian/tibet/tibet.shp"
    chnshp = gpd.read_file(shp_file)
    dz.hours.salem.roi(shape=chnshp).to_netcdf(outfile)    

filelocation = glob.glob("/mnt/qnap/tian/sloar/*.xlsx")
for filename in filelocation:
    excel2sh_nearest(filename)