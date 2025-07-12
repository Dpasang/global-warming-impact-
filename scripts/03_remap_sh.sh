#########################################################################
# File Name: 03_remap_sh.sh
# Author: LIKE NING @ IGSNRR
# mail: ninglk@igsnrr.ac.cn
# Created Time: Sun Nov 27 21:22:21 2022
#########################################################################
#!/bin/bash

# 开启时间统计
starttime=`date +'%Y-%m-%d %H:%M:%S'`
# remap
srcdir=/mnt/f/albedo_3/sh
dstdir=/mnt/f/albedo_3/shr
gridfile=/mnt/f/albedo_3/grid.txt
for file in `ls $srcdir/*.nc`; do
    outfile=${file/$srcdir/$dstdir}
    echo $outfile
    cdo remapbil,$gridfile $file $outfile
done

# 计算运行时间
endtime=`date +'%Y-%m-%d %H:%M:%S'`
start_seconds=$(date --date="$starttime" +%s);
end_seconds=$(date --date="$endtime" +%s);
echo "本次运行时间： "$((end_seconds-start_seconds))"s"
exit
