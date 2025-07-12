#########################################################################
# File Name: 01_bin2nc.sh
# Author: LIKE NING @ IGSNRR
# mail: ninglk@igsnrr.ac.cn
# Created Time: Fri Nov 18 19:22:16 2022
#########################################################################
#!/bin/bash
srcdir=/mnt/syn/albedo_3
tifdir=/mnt/f/albedo_3/tif
ncdir=/mnt/f/albedo_3/nc
mkdir -p $tifdir 
mkdir -p $ncdir
srs_proj4='+proj=sinu +a=6371007.181 +f=0.0 +pm=0 +x_0=0.0 +y_0=0.0 +lon_0=0.0 +units=m +axis=enu +no_defs'
for dir in `ls $srcdir`;do 
    # echo $dir
    input=$srcdir/$dir
    tifname=$tifdir/$dir.tif
    ncname=$ncdir/$dir.nc
    # echo $ncname
    if [ ! -f "$tifname" ]; then
    gdalwarp -overwrite $input $tifname -s_srs $srs_proj4 -t_srs EPSG:4326
    fi
    if [ ! -f "$ncname" ]; then
    gdal_translate -of netCDF -co "FORMAT=NC4" $tifname $ncname
    fi
done
