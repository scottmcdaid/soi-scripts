#Control of Quad box view, Quad or Single Channel
#Copyright 2016, Schmidt Ocean Institute
#Sniffed from "Director Protocol" used by Apantac control software
#Last nibble changes for modes 0x08 = Quad, 0x09 = Ch1, 0x0a = Ch2, 0x0b = Ch3, 0x0c = Ch4

import sys
import select
import time
import socket
import lcm
from gss import pcomms_t,analog_t

QUAD_IP = '10.10.5.98'
QUAD_PORT = 2009
COMMAND = bytearray([0xaa,0xff,0x76,0xa3,0x89,0x5c,0x01,0x00,0x00,0x57,0x08])

TIMEOUT = 1
lcm_count = 0
view = 0

def quad_handler(channel, data):
    global view
    msg = pcomms_t.decode(data)
    print("Message on channel %s" % channel)
    if(msg.num_analogs==1):
        if(msg.analogs[0].name == "VIEW"):
            msg_view = int(msg.analogs[0].value)
            if (msg_view>=0 and msg_view<=4):
                view = msg_view
    return None
    
def quad_status(lc, view):
    global lcm_count
    msg = pcomms_t()
    msg.time_unix_sec = time.time()
    msg.count_publish = lcm_count
    msg.sender_id = "ScottWasHere"
    msg.num_analogs = 1
    msg.num_digitals = 0
    msg.num_messages = 0
    msg.analogs = [analog_t()]
    msg.analogs[0].name = "VIEW"
    msg.analogs[0].value = view
    lc.publish("QUADBOX_STAT", msg.encode())
    lcm_count += 1

lc = lcm.LCM()
lc.subscribe("QUADBOX_CMD", quad_handler)

while True:
    rfds,wfds,efds = select.select([lc.fileno()], [], [], TIMEOUT)
    if rfds:
        lc.handle()
        print "Set Display = %d\n\r" % view
        COMMAND[10] = 0x08 + view #View should already be safe
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((QUAD_IP, QUAD_PORT))
            s.send(COMMAND)
            s.close()
        except:
            print sys.exc_info()[0]
            if s != None:
                s.close()
    print "Loop"
    quad_status(lc,view)
