#!/bin/bash
# $1 - zabbix host (for zabbix-sender)
# $2 - iLO IP
# $3 - iLO username
# $4 - iLO password
/usr/local/bin/python3 /scripts/iLO/hpe_ilo.py "$1" "$2" "$3" "$4"
