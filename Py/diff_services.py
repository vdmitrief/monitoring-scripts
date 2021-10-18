import os
import sys
import cx_Oracle
import difflib
import datetime

con = cx_Oracle.connect('zabbix_user/zabbix_pass@oracle.bla.bla.ru:1527/sid')
cur = con.cursor()
cur.execute('select distinct service from sapsr3.SXMSPFADDRESS')
res = cur.fetchall()

out_string = ""
for result in res:
    out_string += str(result) + "\n"
    #print result
cur.close()
con.close()

out_string = out_string.replace("'","")
out_string = out_string.replace("(","")
out_string = out_string.replace(")","")
out_string = out_string.replace(",","")

##########################################
last_report_path = '/scripts/pip_services.txt'

if os.path.isfile(last_report_path):
    last_report_file = open(last_report_path,'r')
    last_report_str  = last_report_file.read()
    last_report_list = last_report_str.split('\n')

    current_report_list = out_string.split('\n')

    d = difflib.Differ()
    diff = list(d.compare(last_report_list,current_report_list))
    #print '\n'.join(diff)
    # report
    report_line = ""
    for line in diff:
        if line.startswith('+') or line.startswith('-'):
            report_line += line + "\n"

    print report_line
    #with open(current_report, "w") as report_file:
    #    report_file.write("{0}".format(report_line))

with open(last_report_path, "w") as text_file:
    text_file.write("{0}".format(out_string))
