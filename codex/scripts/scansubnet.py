#!/usr/bin/python

# scansubnet.py
# this scripts uses ICMP to ping every host in a specified subnet.
# ========================================================== #
# COLDBLUE
# PETER CHRISTIAN FRAEDRICH
# ========================================================== #

import Queue
import threading
import subprocess as subp
from pymongo import MongoClient
import sys
from socket import gethostbyaddr as rdns
import os
import datetime
from datetime import datetime

console = False

# GET RUNTIME ARGS
if len(sys.argv) == 3 :
	logpath = "./log/py-scansubnet.log"
	range1path = "./scripts/range_1"
	range2path = "./scripts/range_2"
	subnet = sys.argv[2]
	console = False
else :
	logpath = "../log/py-scansubnet.log"
	range1path = "./range_1"
	range2path = "./range_2"
	subnet = sys.argv[1]
	console = True

# SET UP DB CONNECTION
client = MongoClient("mongodb://localhost:27017")
db = client.codex
coll = db.entries

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

def pinger(ip):
	try:
		res = os.system('ping -w 0.5 -c 3' + ip + ' > /dev/null 2>&1')
	except:
		res = 1
	#print ip, response
	if res == 0:
		finder = coll.find_one({'ipaddr':ip})
		print finder
		if finder == None:
			try:
				dns = rdns(ip)[0]
			except:
				dns = ''
			octet = ip.split('.')
			coll.save({"ipaddr":ip, "dnsname":dns, "health":"green.png", "ipA":octet[0], "ipB":octet[1], "ipC":octet[2], "ipD":octet[3], "nickname":"", "subnet":"", "vlan":"", "type":"", "location":"", "notes":"", "reserved":"clear.png"})
			print ip, dns
			#log('200','Found',ip,'in subnet, adding to DB.')
		else:
			print "ip exists, skipping"
			#log('200','IP address exists in DB')

def ping_ip(q, ip):
	q.put(pinger(ip))

# Set up subnet to scan
def setup_subnet(subnet):
	range1 = []
	range2 = []
	subnetlist = []
	a = open(range1path,'r')
	b = open(range2path, 'r')
	for i in a:
		range1.append(str(i))
	for i in b:
		range2.append(str(i))
	net = subnet.split('/')
	netmask = int(net[1])
	octet = net[0].split('.')
	for i in octet:
		i = int(i)
	if netmask == 24:
		if console == True:
			print "Working. This could take between 1 - 30 minutes."
		iprange = octet[0]+'.'+octet[1]+'.'+octet[2]+'.'
		for i in range2:
			subnetlist.append(iprange+i.strip('\n'))
		a.close()
	if netmask == 16:
		if console == True:
			print "Working. This could take between 10 minutes to a few hours depending on your network."
		iprange = octet[0]+'.'+octet[1]+'.'
		for x, y in [(x,y) for x in range1 for y in range2]:
			subnetlist.append(iprange + x.strip('\n') + '.' + y.strip('\n'))
	if netmask == 8:
		if console == True:
			print "Working. This should take a few hours."
		iprange = octet[0]+'.'
		for x, y, z in [(x,y,z) for x in range1 for y in range1 for z in range2]:
			subnetlist.append(iprange + x.strip('\n') + '.' + y.strip('\n') + '.' + z.strip('\n'))
	if netmask == 0:
		if console == True:
			print "WARNING: This should take anywhere between 1 and 5 days to complete."
			yesno = raw_input("Are you sure you want to scan the entire internet? (y/n): ")
			if yesno == "n":
				exit()
		for w, x, y, z in [(w,x,y,z) for w in range1 for x in range1 for y in range1 for z in range2]:
			subnetlist.append(w.strip('\n') + '.' + x.strip('\n') + '.' + y.strip('\n') + '.' + z.strip('\n'))
	return subnetlist

ipaddresses = setup_subnet(subnet)
		
log("INFO",'Creating queue.')
q = Queue.Queue()

for i in ipaddresses:
	t = threading.Thread(target=ping_ip, args = (q,i))
	t.start()

s = q.get()
log("INFO", "Subnet scanner finished scanning.")

exit()