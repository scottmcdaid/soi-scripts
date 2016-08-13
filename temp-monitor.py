#!/usr/bin/env python
#Scrape Temperatures from a BlackBox ServSensor8
#Copyright 2016, Schmidt Ocean Institute

import lcm
import inspect
import time
from pysnmp.hlapi import *
#Magic to open the relative path here
import sys
sys.path.append('/usr/local/share/gss_python_modules/gss')
from gss import pcomms_t,analog_t

IP_ADDR = '10.10.5.99'

lcm_count = 0

def send_lcm_stat(lc,analogs):
    global lcm_count
    msg = pcomms_t()
    msg.time_unix_sec = time.time()
    msg.count_publish = lcm_count
    msg.sender_id = "ScottWasHere"
    msg.num_analogs = 4
    msg.num_digitals = 0
    msg.num_messages = 0
    msg.analogs = analogs
    lc.publish("VAN_TEMP", msg.encode())
    lcm_count += 1

def get_temps(analogs):
    (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) = next(
            getCmd(SnmpEngine(),
                              CommunityData('public',mpModel=0),
                              UdpTransportTarget((IP_ADDR, 161)),
                              ContextData(),
                              ObjectType(ObjectIdentity('1.3.6.1.4.1.3854.1.2.2.1.16.1.1.0')),
                              ObjectType(ObjectIdentity('1.3.6.1.4.1.3854.1.2.2.1.16.1.3.0')),
                              ObjectType(ObjectIdentity('1.3.6.1.4.1.3854.1.2.2.1.16.1.1.1')),
                              ObjectType(ObjectIdentity('1.3.6.1.4.1.3854.1.2.2.1.16.1.3.1')),
                              ObjectType(ObjectIdentity('1.3.6.1.4.1.3854.1.2.2.1.16.1.1.2')),
                              ObjectType(ObjectIdentity('1.3.6.1.4.1.3854.1.2.2.1.16.1.3.2')),
                              ObjectType(ObjectIdentity('1.3.6.1.4.1.3854.1.2.2.1.16.1.1.3')),
                              ObjectType(ObjectIdentity('1.3.6.1.4.1.3854.1.2.2.1.16.1.3.3')),
                              lookupMib=False)
    )
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        print varBinds[0][1]
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))
        analogs[0].name = str(varBinds[0][1])
        analogs[0].value = int(varBinds[1][1])
        analogs[1].name = str(varBinds[2][1])
        analogs[1].value = int(varBinds[3][1])
        analogs[2].name = str(varBinds[4][1])
        analogs[2].value = int(varBinds[5][1])
        analogs[3].name = str(varBinds[6][1])
        analogs[3].value = int(varBinds[7][1])


lc = lcm.LCM()
analogs = [(analog_t()) for _ in range(4)]
while(1):
    print "Publish"
    get_temps(analogs)
    send_lcm_stat(lc, analogs)
    time.sleep(2)
