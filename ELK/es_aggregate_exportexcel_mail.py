import sys
from datetime import datetime,timedelta
from elasticsearch import Elasticsearch
import pandas as pd
import os.path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

##########################################
# SEND e-mail
##########################################
def send_email(subject, message, from_email, to_email=[], attachment=[]):
    """
    :param subject: email subject
    :param message: Body content of the email (string), can be HTML/CSS or plain text
    :param from_email: Email address from where the email is sent
    :param to_email: List of email recipients, example: ["a@a.com", "b@b.com"]
    :param attachment: List of attachments, exmaple: ["file1.txt", "file2.txt"]
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ", ".join(to_email)
    msg.attach(MIMEText(message, 'html'))

    for f in attachment:
        with open(f, 'rb') as a_file:
            basename = os.path.basename(f)
            part = MIMEApplication(a_file.read(), Name=basename)

        part['Content-Disposition'] = 'attachment; filename="%s"' % basename
        msg.attach(part)

    email = smtplib.SMTP('192.168.0.25')
    email.sendmail(from_email, to_email, msg.as_string())

##########################################
# ELASTIC
##########################################
def get_data_es(report_date):
    es = Elasticsearch(['http://log-master.blabla.ru:9200'])

    es_index = 'filebeat-{0}'.format(report_date)

    doc={
          "size":10000,
          "query": {
              "query_string": {
                 "query": "tags:VPN AND !action:failed"
              }
          },

         "aggs" : {
            "group_by_user":{
                "terms":{
                     "field":"user.keyword",
                     "size": 5000
                },
                "aggs":{
                   "group_by_hostname":{
                        "terms":{
                           "field":"hostname.keyword",
                           "size": 20
                        },
                        "aggs":{
                           "group_by_uid":{
                              "terms":{
                                "field":"uid.keyword",
                                "size": 50
                              },
                              "aggs":{
                                 "min_timestamp":{
                                    "min": {"field": "@timestamp"}
                                 },
                                 "max_timestamp":{
                                     "max": {"field": "@timestamp"}.
                                 }
                              }
                           }
                         }
                    }
                 }
              }
          }

    }

    res = es.search(index=es_index, body=doc)
    return res

###############################################
# MAIN
###############################################
curent_weekday = datetime.now().weekday() # 0-6
report_dates = []

if curent_weekday in (1,2,3,4): #Th-Fri
    yesterdate_date = (datetime.now()-timedelta(days=1)).strftime('%Y.%m.%d')
    report_dates.append(yesterdate_date)
elif curent_weekday == 0: #Mon
    sun_date = (datetime.now()-timedelta(days=1)).strftime('%Y.%m.%d')
    sat_date = (datetime.now()-timedelta(days=2)).strftime('%Y.%m.%d')
    fri_date = (datetime.now()-timedelta(days=3)).strftime('%Y.%m.%d')

    report_dates.append(sun_date)
    report_dates.append(sat_date)
    report_dates.append(fri_date)
else:
    sys.exit()

#-------------------------------------------------
for report_date in report_dates:
    res = get_data_es(report_date)
    data = []

    for users in res['aggregations']['group_by_user']['buckets']:
        username = users['key']
        for hosts in users['group_by_hostname']['buckets']:
            host = hosts['key']
            for uids in hosts['group_by_uid']['buckets']:
                uid = uids['key']
                min_time = datetime.strptime(uids['min_timestamp']['value_as_string'],"%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=5)
                max_time = datetime.strptime(uids['max_timestamp']['value_as_string'],"%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=5)
                duration = (uids['max_timestamp']['value'] - uids['min_timestamp']['value'])/1000
                #print u'{0} {1} {2} {3} {4} {5}'.format(username, host, uid, min_time, max_time, duration)
                data.append([username, host, uid, min_time, max_time, duration])
        #sys.exit()
        #break

    df = pd.DataFrame(data, columns=['username', 'hostname', 'uid', 'start time', 'end time', 'duration'])
    df.to_excel("/scripts/vpn/vpn_{0}.xlsx".format(report_date))

    send_email('vpn-{0}'.format(report_date), 'Hello, sent from es-master.blabla.ru (cron)', 'zabbix@blabla.ru', ['user1@blabla.ru','user2@blabla'], ["/scripts/vpn/vpn_{0}.xlsx".format(report_date)])


