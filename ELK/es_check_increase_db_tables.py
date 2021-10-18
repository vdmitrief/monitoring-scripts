#-*- coding: utf-8 -*-
import sys
import os
import json
from datetime import datetime
from elasticsearch import Elasticsearch

##########################################
#    ELASTIC
es = Elasticsearch([{'host':'log-master.bla.ru','port':9200}])

es_index = 'db.statistic-*'
database_alias = sys.argv[1]

#########################################
data_rows={}

##########################################
# GET DATA
search_string='_exists_:bytes AND type:"db.statistic.{0}.tables.size" AND (@timestamp:[now-1d TO now] OR @timestamp:[now-7d TO now-6d] OR @timestamp:[now-30d TO now-29d] OR @timestamp:[now-60d TO now-59d])'.format(database_alias)
doc={
     "query": {
                "query_string":{
                                "query":search_string
                               }
              },
     "sort" : [{ "@timestamp" : "asc" }]
    }
page = es.search(
          index = es_index,
          size = 1000,
          scroll='2m',
          body = doc
      )

sid = page['_scroll_id']
scroll_size = page['hits']['total']

#print scroll_size
#sys.exit()

###########################################
my_dict={}
while (scroll_size > 0):
    for hit in page['hits']['hits']:

        if my_dict.has_key(hit['_source']['owner']) != 1:
            my_dict[hit['_source']['owner']]={}

        if my_dict[hit['_source']['owner']].has_key(hit['_source']['segment_name']) != 1:
            my_dict[hit['_source']['owner']][hit['_source']['segment_name']]=[]

        my_dict[hit['_source']['owner']][hit['_source']['segment_name']].append(hit['_source']['bytes'])

    page = es.scroll(scroll_id = sid, scroll = '2m')
    sid = page['_scroll_id']
    scroll_size = len(page['hits']['hits'])

#print my_dict
###########################################
# PREPARE RESULTS
result = ''

for owner, tables in my_dict.items():
    for tablename, rows in tables.items():
        #if rows[0]<>rows[1]<>rows[2]:
        #    print '{}:{} -- {}'.format(owner,tablename,rows)
        #    sys.exit()

        #diff_rows = round(float(rows[-1] - rows[0])/rows[0],2)
        #print u'{} {}'.format(tablename,rows)
        if rows[0] == 0:
            result +='{}:{} - dropped\n'.format(owner,tablename)
        else:
            diff_rows = round(float(rows[-1])/float(rows[0]),3)

            if diff_rows>1.5 and rows[-1]>200000000: #процент больше 20% и только для таблиц более 200 МБ
                result +='{}:{} - {}% (size [60d,30d,7d,now] {} bytes)\n'.format(owner,tablename,diff_rows*100,rows)
#
if len(result)>0:
    print result
else:
    print '0x0'
