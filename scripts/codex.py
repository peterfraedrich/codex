#!/usr/bin/python
#
# CODEX MODULES
# ========================================================== #
# COLDBLUE
# PETER CHRISTIAN FRAEDRICH
# ========================================================== #

from os import path
from datetime import datetime
from pymongo import MongoClient

def db_connect():
	client = MongoClient("mongodb://localhost:27017")
	db = client.codex
	coll = db.entries
	return coll

def log(code, message, logpath):
# check if log exists, if not, create it
	if path.exists(logpath):
		# check log file for length
		r = open(logpath,'r')
		if path.getsize(logpath) > 5000000.0:
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
