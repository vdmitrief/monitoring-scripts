#!/bin/bash
JSON="{ \"data\":["
DG=(`vxstat -o alldgs | awk -F'^DG' '{print $2}' | sed '/^$/d;s/ //'`)
for VAR in ${DG[@]}; do
VOL=(`vxstat -g $VAR | grep ^vol | awk '{print $2}'`)
c=`echo ${#VOL[@]}`
contents=(`echo ${VOL[@]}`)
if [[ ${#VOL[@]} -gt 1 ]]; then
 for VAR1 in ${contents[@]}; do
 JSON=${JSON}"{ \"{#DG}\":\"${VAR[0]}_${VAR1[0]}\"},"
 done
else
JSON=${JSON}"{ \"{#DG}\":\"${VAR[0]}_${VOL[0]}\"},"
fi
done
JSON=${JSON}"]}"
echo $JSON | sed 's/,]}/]}/'
