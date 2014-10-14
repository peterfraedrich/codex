#!/usr/bin/python

# import.py
# this script imports hosts from CSV into the DB.
# ========================================================== #
# COLDBLUE
# PETER CHRISTIAN FRAEDRICH
# ========================================================== #

# imports
from pymongo import MongoClient
import sys
import os
import datetime
from datetime import datetime
import socket

logpath = '../log/py-import.log'

def log(code, message):
    # check if log exists, if not, create it
    if os.path.exists(logpath):
        # check log file for length
        r = open(logpath,'r')
        if os.path.getsize(logpath) > 5000000.0:
            w = open(logpath +'.old','w')
            for i in r:
                w.write(i)
            w.close()
        r.close()
    else:
        w = open(logpath,'w')
        w.close()
    d = str(datetime.now().strftime("%m:%d:%Y::%H:%M.%S"))
    a = open(logpath, 'a')
    a.write(d + " -- " + code + " -- " + message + "\n")
    a.close()

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
        print "  [ipaddress],[hostname],[subnet mask],[VLAN],[login]"
        print "  ex.: 10.10.0.1,Test Computer,255.255.0.0,10,username/password"
        sys.exit() 
    elif sys.argv[1] == "help" :
        print "Import supports the following format for imported files:"
        print "  [ipaddress],[hostname],[subnet mask],[VLAN],[login]"
        print "  ex.: 10.10.0.1,Test Computer,255.255.0.0,10,username/password"
        sys.exit()
    else:
        print "Import supports the following format for imported files:"
        print "  [ipaddress],[hostname],[subnet mask],[VLAN],[login]"
        print "  ex.: 10.10.0.1,Test Computer,255.255.0.0,10,username/password"
        sys.exit() 

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client.codex
coll = db.entries

added = 0

print ""
path = raw_input("Type the ABSOLUTE path to the delineated list you wish to import: ")
delineator = raw_input("What character is used to separate the items (comma or semicolon is recommended)? ")
exit = raw_input(bcolors.red + "These hosts will be assumed to be up. Do you wish to continue? (y/n) " + bcolors.ENDC)

if exit == 'n' :
    sys.exit()

csv = [line.strip() for line in open(path)]

#print csv

for i in csv :

    split = i.split(delineator)
    ipaddr = split[0]
    nickname = split[1]
    subnet = split[2]
    vlan = split[3]
    login = split[4]
    date = str(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

    save = ({
        "ipaddr": ipaddr,
        "hostname": hostname,
        "subnet": subnet,
        "vlan": vlan,
        "login": login,
        "user": "system import",
        "alive": "True",
        "ping": "0",
        "pingfail": "0",
        "added": date,
        "lastalive": date,
        "lastscan": date,
        "health": "100",
        "tidyflag": "False",
        "reserved": "False"
        })

    #print save
    coll.insert(save)
    added = added + 1
    print bcolors.green + "   Host " + ipaddr + " / " + hostname + " added to the DB." + bcolors.ENDC


# write to log @ start
log("101","Import completed. Imported " + added + "entries.")








