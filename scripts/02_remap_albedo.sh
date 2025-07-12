#########################################################################
# File Name: 02_remap_albedo.sh
# Author: LIKE NING @ IGSNRR
# mail: ninglk@igsnrr.ac.cn
# Created Time: Sat Nov 19 16:20:33 2022
#########################################################################
#!/bin/bash
# 开启时间统计
starttime=`date +'%Y-%m-%d %H:%M:%S'`
# remap
srcdir=/home/ninglk/Chooyu/new_albedo
dstdir=/home/ninglk/Chooyu/1_albedo/2Apr25/albedo_yr
gridfile=/home/ninglk/Chooyu/1_albedo/2Apr25/scripts/albedo.grid
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
