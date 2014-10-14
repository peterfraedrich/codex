#!/usr/bin/python

# deleteall.py
# drops the table in the DB. THIS CANNOT BE UNDONE. DONT RUN
# UNLESS YOU'RE REALLY SURE THIS IS WHAT YOU WANNA DO.
# ========================================================== #
# COLDBLUE
# PETER CHRISTIAN FRAEDRICH
# ========================================================== #

from pymongo import MongoClient
import sys
import os
import datetime
from datetime import datetime

console = False

# GET RUNTIME ARGS
if len(sys.argv) > 1 :
	if sys.argv[1] == "-node" : # -node flag sets new path for log files since script is launched from app root
		logpath = "./log/py-deleteall.log"
else:
	console = True
	logpath = "..log/py-deleteall.log"

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

# SET UP DB CONNECTION
client = MongoClient("mongodb://localhost:27017")
db = client.codex
coll = db.entries


if console == True:
	log('998',"Someone wants to delete everything. Making sure they're sure.")
	print "Are you sure you want to delete all entries?"
	print "WARNING: THIS CANNOT BE UNDONE."
	yesno = raw_input("(y/n): ")
	if yesno == "y":
		sure = raw_input("Are you sure? (y/n): ")
		if sure == "y":
			coll.drop()
			log('999','Entries table dropped. I guess they were sure.')
			print "Everything deleted!"
			print "I hope you had backups..."
			exit()
		else:
			log('997','Delete operation aborted.')
			print "Aborting."
			exit() 
	else:
		log('996','Delete operation aborted.')
		print "Aborting."
		exit()
else:
	coll.drop()
	log('999','Entries table dropped by the NODE server, presumably because someone told it to; otherwise Skynet has taken over and you should probably go find a place to hide.')
	exit()