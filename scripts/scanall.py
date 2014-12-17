#!/usr/bin/python

# scanall.py
# this script crawls the DB to make sure the hosts are up.
# ========================================================== #
# COLDBLUE
# PETER CHRISTIAN FRAEDRICH
# ========================================================== #

import Queue
import threading
import subprocess as subp
from socket import gethostbyaddr as rdns
import sys
import os
from codex import log, db_connect

db = db_connect()
rows  = db.find()

# GET RUNTIME ARGS
if len(sys.argv) > 1 :
	if sys.argv[1] == "-node": # -node flag sets new path for log files since script is launched from app root
		logpath = "./log/py-scanall.log"
else :
	logpath = "../log/py-scanall.log"

def pinger(ip, health):
	try:
		res = os.system('ping -W 1 -c 1 ' + ip + ' > /dev/null 2>&1')
	except:
		log("ERROR","ICMP transmit error.", logpath)
		res = 1
	#print ip, response
	if res == 0:
		try:
			dns = rdns(ip)[0]
		except:
			dns = ''
		reserved = db.find_one({'ipaddr':ip})
		if reserved['reserved'] == 'reserved.png':
			resupdate = 'clear.png'
		else:
			resupdate = 'reserved.png'
		db.update( {"ipaddr": ip}, {"$set" : {"health":"green.png","dnsname":dns,"reserved":resupdate} } )
	else:
		db.update( {"ipaddr": ip}, {"$set" : {"health":"red.png"} } )

# called by each thread
def ping_ip(q, row):
	ip = row['ipaddr']
	health = row['health']
	q.put(pinger(ip,health))

log("INFO",'Creating queue.', logpath)
q = Queue.Queue()

for i in rows:
	t = threading.Thread(target=ping_ip, args = (q,i))
	t.start()

s = q.get()
log("INFO", "db_crawler finished crawling.", logpath)

exit()