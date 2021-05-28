#!/bin/bash
#UserParameter=elasticsearch.index.size[*],/etc/zabbix/index_size.sh $1
index_name=$1
curl http://127.0.0.1:9200/$index_name-*/_stats/store 2>&1 | grep -o "_all\":{\"primaries\":{\"store\":{\"size_in_bytes\":[0-9]\{1,99\}}}," | grep -o "[0-9]\{1,99\}"
