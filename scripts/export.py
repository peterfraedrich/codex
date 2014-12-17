#!/usr/bin/python

# export.py
# this script exports the database to .CSV for saving
# ==============================================================#
# COLDBLUE
# PETER CHRISTIAN FRAEDRICH
# ==============================================================#

from codex import db_connect
from os import path
from datetime import datetime
import Queue
import threading
import subprocess as subp

db = db_connect()
rows = db.find()

print ''
print '############ Welcome to the CODEX database export tool ############'
print ''
print '--- this will NOT affect your Codex install or database entries ---'
print ''
print '###################################################################'
print ''

def get_path():
	print 'Enter the ABSOLUTE path where you would like to export the database:'
	global export_path
	export_path = raw_input('> ')
	#end

def check_path(fpath):
	d = str(datetime.now().strftime("%m%d%Y"))
	fname = str(fpath) +'/' + 'codex_export_'+d
	if path.exists(fname):
		overwrite = raw_input("File exists. Overwrite? (y/n):")
		if str(overwrite) == "y":
			export(fname)
		else:
			get_path()
	else:
		export(fname)
	#end

def create_file(fname):
	w = open(fname, 'w')
	w.close()

def write_model(fname):
	w = open(fname, 'a')
	w.write('IP Address,Nickname,DNS Name,Type,Subnet,VLAN,Reserved,Health,Notes'+'\n')
	w.close()

def thread_start(q,fname,data):
	q.put(write_to_file(fname,data))

def write_to_file(fname, data):
	w = open(fname, 'a')
	ip = str(data['ipaddr'])
	nickname = str(data['nickname'])
	dnsname = str(data['dnsname'])
	subnet = str(data['subnet'])
	itemtype = str(data['type'])
	vlan = str(data['vlan'])
	notes = str(data['notes'])
	if str(data['reserved']) == 'clear.png':
		reserved = 'no'
	else:
		reserved = 'yes'
	if str(data['health']) == 'green.png':
		health = 'up'
	else:
		health = 'down'

	to_write = ip + ',' + nickname + ',' + dnsname + ',' + itemtype + ',' + subnet + ',' + vlan + ',' + reserved + ',' + health + ',' + notes + '\n'
	w.write(to_write)
	w.close()
	print "Entry " + ip + ' ' + nickname + ' saved.'

def export(fname):
	create_file(fname)
	write_model(fname)

	print "Starting export..."
	for i in rows:
		write_to_file(fname, i)

get_path()
check_path(export_path)
exit()