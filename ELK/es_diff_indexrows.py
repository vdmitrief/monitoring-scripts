#-*- coding: utf-8 -*-
import sys
import os
from datetime import datetime
from elasticsearch import Elasticsearch

##########################################
#    ELASTIC
es = Elasticsearch([{'host':'log-master.blablabla.ru','port':9200}])

es_index = 'db.statistic-*'
database_alias = sys.argv[1]

#########################################
tablerows_now={}
tablerows_yst={}

##########################################
# GET TABLES NOW
search_string='_exists_:num_rows AND type:"db.statistic.{0}.indexes.rows" AND @timestamp:[now-24h TO now]'.format(database_alias)
doc={
     "query": {
                "query_string":{
                                "query":search_string
                               }
              }
    }
page = es.search(
          index = es_index,
          size = 1000,
          scroll='2m',
          body = doc
      )

sid = page['_scroll_id']
scroll_size = page['hits']['total']

while (scroll_size > 0):
    for hit in page['hits']['hits']:
        tablerows_now['{0} {1}'.format(hit['_source']['owner'],hit['_source']['index_name'])]= hit['_source']['num_rows']
    # go to next page if it exist ->
    page = es.scroll(scroll_id = sid, scroll = '2m')
    sid = page['_scroll_id']
    scroll_size = len(page['hits']['hits'])

##########################################
# GET TABLES YESTERDAY
search_string='_exists_:num_rows AND type:"db.statistic.{0}.indexes.rows" AND @timestamp:[now-48h TO now-24h]'.format(database_alias)
doc={
     "query": {
               "query_string":{
                              "query":search_string
                              }
              }
    }
page = es.search(
                index = es_index,
                size = 1000,
                scroll='2m',
                body = doc
                )

sid = page['_scroll_id']
scroll_size = page['hits']['total']

while (scroll_size > 0):
    for hit in page['hits']['hits']:
        tablerows_yst['{0} {1}'.format(hit['_source']['owner'],hit['_source']['index_name'])]= hit['_source']['num_rows']
    # go to next page if it exist ->
    page = es.scroll(scroll_id = sid, scroll = '2m')
    sid = page['_scroll_id']
    scroll_size = len(page['hits']['hits'])

###########################################
# PREPARE RESULTS
row_id = int(datetime.now().strftime('%s'))*1000
es_index = es_index.replace('*', datetime.now().strftime("%Y.%m.%d"))

for key, value in tablerows_yst.items():
    try:
        change_abs = int(tablerows_now[key])-int(value)
        if int(value)==0:
            change_prc = 0
        else:
            change_prc = change_abs*100/int(value)

        #write to elastic
        if change_abs != 0:
            es_list={}
            es_list['type']   = "db.statistic.{0}.indexes.rows.diff".format(database_alias)
            es_list['@timestamp'] = datetime.now().isoformat() + "+05:00"
            es_list['index_name']   = key
            es_list['diff_rows']   = int(change_abs)
            es_list['diff_rows_percent']   = int(change_prc)
            es.index(index=es_index,doc_type='doc',id=row_id,body=es_list)
            row_id +=1
    except KeyError:
        #print u'{0} --- {1} ---- {2}'.format(key,value,"DROPPED")
        es_list={}
        es_list['type']   = "db.statistic.{0}.indexes.new".format(database_alias)
        es_list['@timestamp'] = datetime.now().isoformat() + "+05:00"
        es_list['index_names']   = key
        es.index(index=es_index,doc_type='doc',id=row_id,body=es_list)
        row_id +=1
