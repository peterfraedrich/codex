#!/usr/bin/python

# import.py
# this script imports hosts from CSV into the DB.
# ========================================================== #
# COLDBLUE
# PETER CHRISTIAN FRAEDRICH
# ========================================================== #

# imports
import Queue
import threading
import subprocess as subp
import sys
import os
from socket import gethostbyaddr as rdns
import socket
from codex import log, db_connect

logpath = '../log/py-import.log'
entries = 0
skipped = 0

db = db_connect()

# for color-y texty goodness
class bcolors:
    grey = '\033[0;30m'
    greybold = '\033[1;30m'
    red = '\033[0;31m'
    redbold = '\033[1;30m'
    green = '\033[0;32m'
    greenbold = '\033[1;32m'
    ENDC = '\033[0m'

    def disable(self):
        self.END = ''
        self.greybold = ''
        self.red = ''
        self.redbold = ''
        self.green = ''
        self.greenbold = ''

# get args
if len(sys.argv) > 1 :
    if sys.argv[1] == "-h" :
        print "Import supports the following format for imported files:"
        print "  [IP Address],[Nickname],[Subnet],[VLAN ID],[Location],[Reserved],[Notes]"
        print "  ex.: 192.168.1.1,router,192.168.0.1/24,10,server room,no,admin/abcd1234"
        sys.exit() 
    elif sys.argv[1] == "help" :
        print "Import supports the following format for imported files:"
        print "  [IP Address],[Nickname],[Subnet],[VLAN ID],[Location],[Reserved],[Notes]"
        print "  ex.: 192.168.1.1,router,192.168.0.1/24,10,server room,no,admin/abcd1234"
        sys.exit()
    else:
        print "Import supports the following format for imported files:"
        print "  [IP Address],[Nickname],[Subnet],[VLAN ID],[Location],[Reserved],[Notes]"
        print "  ex.: 192.168.1.1,router,192.168.0.1/24,10,server room,no,admin/abcd1234"
        sys.exit() 

print ""
path = raw_input("Type the ABSOLUTE path to the delineated list you wish to import: ")
delineator = raw_input("What character is used to separate the items (comma or semicolon is recommended)? ")

csv = [line.strip() for line in open(path)]

def import_csv(row):
    global entries
    global skipped
    global existed
    split = row.split(delineator)
    if len(split) > 4:
        ipaddr = split[0]
        nickname = split[1]
        subnet = split[2]
        vlan = split[3]
        location = split[4]
        notes = split[6]
        if split[5].lower() == "true" or split[5].lower() == "yes" or split[5].lower() == 'reserved':
            reserved = 'reserved.png'
        else:
            reserved = 'clear.png'
        octet = ipaddr.split('.')
        try:
            dns = rdns(ipaddr)[0]
        except:
            dns = ''   
        try:
            res = os.system('ping -W 1 -c 1 ' + ipaddr + ' > /dev/null 2>&1')
        except:
            res = 1
        #print ip, response
        if res == 0:
            health = 'green.png'
            reserved = 'clear.png'
        else:
            health = 'red.png'
        save = ({
            "ipaddr":ipaddr, 
            "nickname":nickname, 
            "dnsname": dns,
            "subnet":subnet, 
            "vlan":vlan, 
            "location":location,
            "notes":notes,  
            "ipA":octet[0], 
            "ipB":octet[1], 
            "ipC":octet[2], 
            "ipD":octet[3], 
            "health":health, 
            "reserved":reserved
            })
        #print save
        exist = db.find_one({"ipaddr":ipaddr})
        if exist == None:
            db.insert(save)
            entries = entries + 1
            print bcolors.green + "   Host " + ipaddr + " / " + nickname + " added to the DB." + bcolors.ENDC
    else:
        skipped = skipped + 1

def worker(q,row):
    q.put(import_csv(row))

log("INFO",'Creating queue.', logpath)
q = Queue.Queue()

added = 0

for i in csv:
    t = threading.Thread(target=worker, args = (q,i))
    t.start()

s = q.get()
print bcolors.green + str(added) + " entries added to the codex." + bcolors.ENDC
print bcolors.red +  str(skipped) + " entries skipped because they did not meet the formatting requirements." + bcolors.ENDC


# write to log @ start
log("101","Import completed. Added " + str(entries) + " entries to the codex. " + str(skipped) + " skipped.", logpath)


sys.exit()







