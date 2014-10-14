#!/usr/bin/python

# host-checker
###########################
# ColdBlue USA
# Peter Christian Fraedrich
###########################
#
#
# imports
#from pymongo import MongoClient
import sys
import socket
import os
import datetime
from datetime import datetime

# MongoDB connection
#client = MongoClient(config_dburl)
#db = client.stv2
#coll = db.hosts

# write to log @ start
#f = open('/stv2/scripts/logfile','a')
#f.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : node.js kicked off the host checker successfully.\n")
#f.close()

# define vars
count = 0
alive = False

# get stdin from node server
stdin = sys.stdin.readlines()
for i in stdin:
	host = i.strip('\n')
print ip  ### DEBUG

# ping host to see if it's up
for i in 3:
	response = os.system("ping -w 1 -c 1 " + ipaddr + " > /dev/null 2>&1")
	count = count + 1

if count > 1:
	alive = True

# get DNS lookup
hostname_long = socket.gethostbyaddr(ip)
hostname = hostname_long[0]

print hostname ### DEBUG

stdout = sys.stdout.write('{ ip:"'+ip+'",hostname:"'+hostname+'",alive:"'+alive+'"}')

exit()