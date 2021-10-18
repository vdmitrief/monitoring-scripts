# -*- coding: utf-8 -*-
# use <script.py> zabbix_host ilo_ip ilo_username ilo_password
import sys
import redfish
from pyzabbix import ZabbixMetric, ZabbixSender

##########################################################
#                   INIT
#########################################################
ZABBIX_IP = '127.0.0.1'
ZABBIX_HOSTNAME = sys.argv[1]

ILO_IP = sys.argv[2]
ILO_USER = sys.argv[3]
ILO_PASS = sys.argv[4]


ilo_hostname                 = ''
ilo_model                    = ''
ilo_BiosOrHardwareHealth     = ''
ilo_FanRedundancy            = ''
ilo_Fans                     = ''
ilo_Memory                   = ''
ilo_Network                  = ''
ilo_PowerSupplies            = ''
ilo_PowerSupplyRedundancy    = ''
ilo_Processors               = ''
ilo_SmartStorageBattery      = ''
ilo_Storage                  = ''
ilo_Temperatures             = ''
ilo_CurrentPowerOnTimeSeconds= 0
ilo_ProcessorSummary         = 0
ilo_CPUUtil                  = 0
ilo_SerialNumber             = ''
ilo_Status                   = ''

REDFISH_OBJ = redfish.redfish_client(base_url='https://{0}'.format(ILO_IP), username=ILO_USER, password=ILO_PASS)
REDFISH_OBJ.login()

obj_response = REDFISH_OBJ.get("/redfish/v1/systems/1")

###########################################################
#                   COOLECT DATA
###########################################################
try:
    ilo_hostname             = obj_response.obj['HostName']
    ilo_model                = obj_response.obj['Model']
    ilo_ProcessorSummary     = obj_response.obj['ProcessorSummary']['Count']
    ilo_SerialNumber         = obj_response.obj['SerialNumber']
    ilo_Status               = obj_response.obj['Status']['Health']
except:
    print('No obj Inventory')

try:
    ilo_BiosOrHardwareHealth = obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['BiosOrHardwareHealth']['Status']['Health']
    ilo_FanRedundancy        = obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['FanRedundancy']
    ilo_Fans                 = obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['Fans']['Status']['Health']
    ilo_Memory               = obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['Memory']['Status']['Health']
    ilo_Network              = obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['Network']['Status']['Health']
    ilo_PowerSupplies        = obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['PowerSupplies']['Status']['Health']
    ilo_PowerSupplyRedundancy= obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['PowerSupplyRedundancy']
    ilo_Processors           = obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['Processors']['Status']['Health']
    ilo_SmartStorageBattery  = obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['SmartStorageBattery']['Status']['Health']
    ilo_Storage              = obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['Storage']['Status']['Health']
    ilo_Temperatures         = obj_response.obj['Oem']['Hpe']['AggregateHealthStatus']['Temperatures']['Status']['Health']
except:
    print('No obj component status')

try:
    ilo_CurrentPowerOnTimeSeconds= obj_response.obj['Oem']['Hpe']['CurrentPowerOnTimeSeconds']
    ilo_CPUUtil              = obj_response.obj['Oem']['Hpe']['SystemUsage']['CPUUtil']
except:
    print('No obj perf metrics')

#################################################################
#                      SEND METRICS
#################################################################
metrics=[]

metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.hostname", ilo_hostname))
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.model",    ilo_model))
#-------------------------------------------
if ilo_BiosOrHardwareHealth == 'OK':
    ilo_BiosOrHardwareHealth = 1
else:
    ilo_BiosOrHardwareHealth = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.BiosOrHardwareHealth", ilo_BiosOrHardwareHealth))
#--------------------------------------------
if ilo_FanRedundancy == 'Redundant':
    ilo_FanRedundancy = 1
else:
    ilo_FanRedundancy = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.FanRedundancy", ilo_FanRedundancy))
#--------------------------------------------
if ilo_Fans == 'OK':
    ilo_Fans = 1
else:
    ilo_Fans = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.Fans", ilo_Fans))
#--------------------------------------------
if ilo_Memory == 'OK':
    ilo_Memory = 1
else:
    ilo_Memory = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.Memory", ilo_Memory))
#--------------------------------------------
if ilo_Network == 'OK':
    ilo_Network = 1
else:
    ilo_Network = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.Network", ilo_Network))
#--------------------------------------------
if ilo_PowerSupplies == 'OK':
    ilo_PowerSupplies = 1
else:
    ilo_PowerSupplies = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.PowerSupplies)", ilo_PowerSupplies))
#--------------------------------------------
if ilo_PowerSupplyRedundancy == 'Redundant':
    ilo_PowerSupplyRedundancy = 1
else:
    ilo_PowerSupplyRedundancy = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.PowerSupplyRedundancy", ilo_PowerSupplyRedundancy))
#--------------------------------------------
if ilo_Processors == 'OK':
    ilo_Processors = 1
else:
    ilo_Processors = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.Processors", ilo_Processors))
#--------------------------------------------
if ilo_SmartStorageBattery == 'OK':
    ilo_SmartStorageBattery = 1
else:
    ilo_SmartStorageBattery = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.SmartStorageBattery", ilo_SmartStorageBattery))
#--------------------------------------------
if ilo_Storage == 'OK':
    ilo_Storage = 1
else:
    ilo_Storage = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.Storage", ilo_Storage))
#--------------------------------------------
if ilo_Temperatures == 'OK':
    ilo_Temperatures = 1
else:
    ilo_Temperatures = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.Temperatures", ilo_Temperatures))
#--------------------------------------------
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.CurrentPowerOnTimeSeconds", ilo_CurrentPowerOnTimeSeconds))
#--------------------------------------------
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.ProcessorSummary", ilo_ProcessorSummary))
#--------------------------------------------
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.CPUUtil", ilo_CPUUtil))
#--------------------------------------------
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.SerialNumber", ilo_SerialNumber))
#--------------------------------------------
if ilo_Status == 'OK':
    ilo_Status = 1
else:
    ilo_Status = 0
metrics.append(ZabbixMetric(ZABBIX_HOSTNAME,"ilo.Status", ilo_Status))

data = ZabbixSender(ZABBIX_IP)
data.send(metrics)
#print(metrics)

##################################################################
REDFISH_OBJ.logout()
print(1)
