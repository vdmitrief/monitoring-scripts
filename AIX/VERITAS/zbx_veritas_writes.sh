#!/bin/bash
param=$1
dg=`echo $param | sed s'/_.*//'`
vol=`echo $param | sed s'/.*_//'`
vxstat -g $dg -i 1 -c 2 | grep " $vol" | awk '{print $8}' | tail -n 1
