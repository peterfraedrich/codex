#!/usr/bin/python

# scanone.py
# this script scans a single entry. Can be run from the
# command line using the IP as a single argument.
# ========================================================== #
# COLDBLUE
# PETER CHRISTIAN FRAEDRICH
# ========================================================== #

from socket import gethostbyaddr as rdns
import sys
import os
from codex import log, db_connect

db = db_connect()

console = False

# GET RUNTIME ARGS
if len(sys.argv) > 2:
	if sys.argv[1] == "-node" : # -node flag sets new path for log files since script is launched from app root
		logpath = "./log/py-scanone.log"
		ip = sys.argv[2]
	else:
		print "If using more than 1 arguments, first argument must be '-node'."
		exit()
elif len(sys.argv) > 1:
	ip = sys.argv[1]
	console = True
	logpath = "../log/py-scanone.log"
else:
	print "This script takes exactly one or two arguments. If two, the first argument must be '-node'."
	exit()

if console == True:
	log("INFO","Starting ping to " + ip, logpath)
	try:
		res = os.system('ping -W 1 -c 1 ' + ip)
	except:
		log("ERROR","ICMP transmit error.", logpath)
		res = 1
	if res == 0:
		try:
			dns = rdns(ip)[0]
		except:
			dns = ''
		reserved = db.find_one({'ipaddr':ip})
		if reserved['reserved'] == "reserved.png":
			resupdate = "clear.png"
		else:
			resupdate = "reserved.png"
		db.update({"ipaddr": ip}, {"$set": {"health":"green.png", "dnsname":dns, "reserved":resupdate}})
		log("INFO","Finished checking " + ip, logpath)
		sys.exit()
	else:
		db.update({"ipaddr": ip}, {"$set": {"health":"red.png"}})
		log("INFO","Finished checking " + ip, logpath)
		sys.exit()
else:
	log("INFO","Starting ping to " + ip)
	try:
		res = os.system('ping -W 1 -c 1 ' + ip + ' > /dev/null 2>&1')
	except:
		log("ERROR","ICMP transmit error.", logpath)
		res = 1
	if res == 0:
		try:
			dns = rdns(ip)[0]
		except:
			dns = ''  
		db.update( {"ipaddr": ip}, {"$set" : {"health":"green.png", "dnsname":dns} } )
		log("INFO","Finished checking " + ip, logpath)
		exit()
	else:
		db.update( {"ipaddr": ip}, {"$set" : {"health":"red.png"} } )
		log("INFO","Finished checking " + ip, logpath)
		exit()