#!/usr/bin/python
#
# cambridge.py // db host auto-scanner
###########################
# ColdBlue USA
# Peter Christian Fraedrich
###########################
#
#

# imports
from pymongo import MongoClient
import sys
import os
import datetime
from datetime import datetime
import subprocess
import threading

# write to log @ start
f = open('/stv2/scripts/logfile','a')
f.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : Cambridge started successfully.\n")
f.close()

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


# get arguments & set flags
interactive_mode = False

if len(sys.argv) > 1 :
    if sys.argv[1] == "-i" :
        interactive_mode = True
    elif sys.argv[1] == "interactive" :
        interactive_mode = True
    elif sys.argv[1] == "-h" :
        print """Cambridge supports two modes: silent and interactive. For interactive mode, run with argument "-i" """
        sys.exit() 
    elif sys.argv[1] == "help" :
        print """Cambridge supports two modes: silent and interactive. For interactive mode, run with argument "-i" """
        sys.exit()
    else:
        print """Cambridge supports two modes: silent and interactive. For interactive mode, run with argument "-i" """
        sys.exit() 


# translate vars because I'm lazy
imode = interactive_mode

if imode == True :
    os.system("clear")
    print bcolors.red + "Welcome to the Cambridge auto-scanner." + bcolors.ENDC + "\n"


######### import options from config file
optionfile = [line.strip() for line in open('/stv2/scripts/cambridge_conf')]

# check for enterprise lic
if optionfile[1] == "4444026290" :
    enterprise = True

# sets how long to keep dead hosts before removal
config_keephosts = optionfile[4]

# enable using external DB for enterprise versions
if enterprise == True :
    config_dburl = optionfile[7]
else:
    config_dburl = "mongodb://localhost:27017"

if imode == True :
    print bcolors.green + "Enterprise license key " + optionfile[1] + " recognized. Enabling paid features." + bcolors.ENDC
    print ""

# MongoDB connection
client = MongoClient(config_dburl)
db = client.stv2
coll = db.hosts


# get number of items in db
rows = coll.count()


# set iterator to 0
i = 0

#####################
#####################
class Pinger(object):
    status = {'alive': [], 'dead': []} # Populated while we are running
    hosts = [] # List of all hosts/ips in our input queue

    # How many ping process at the time.
    thread_count = 4

    # Lock object to keep track the threads in loops, where it can potentially be race conditions.
    lock = threading.Lock()

    def ping(self, ip):
        # Use the system ping command with count of 1 and wait time of 1.
        ret = subprocess.call(['ping', '-c', '1', '-W', '1', ip],
                              stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))

        return ret == 0 # Return True if our ping command succeeds

    def pop_queue(self):
        ip = None

        self.lock.acquire() # Grab or wait+grab the lock.

        if self.hosts:
            ip = self.hosts.pop()

        self.lock.release() # Release the lock, so another thread could grab it.

        return ip

    def dequeue(self):
        while True:
            ip = self.pop_queue()

            if not ip:
                return None

            result = 'alive' if self.ping(ip) else 'dead'
            self.status[result].append(ip)

    def start(self):
        threads = []

        for i in range(self.thread_count):
            # Create self.thread_count number of threads that together will
            # cooperate removing every ip in the list. Each thread will do the
            # job as fast as it can.
            t = threading.Thread(target=self.dequeue)
            t.start()
            threads.append(t)

        # Wait until all the threads are done. .join() is blocking.
        [ t.join() for t in threads ]

        return self.status

##################
##################


# iterate through rows in db
while i < rows :

    # get row of db at index i
    result = coll.find()[i]

    # assign elements to vars
    ip = str(result['ipaddr'])
    alive = bool(result['alive'])
    ping = int(result['ping'])
    pingfail = int(result['pingfail'])
    health = int(result['health'])
    lastscan = str(result['lastscan'])
    reserved = bool(result['reserved'])
    hostname = str(result['hostname'])
    user = str(result['user'])
    added = str(result['added'])
    tidyflag = bool(result['tidyflag'])
    lastalive = str(result['lastalive'])
    login = str(result['login'])
    subnet = str(result['subnet'])
    vlan = str(result['vlan'])
    
    if imode == True :
        print "Got index " + str(i+1) + " of " + str(rows) + "; waiting for ping test..."

    ######## debug
    if imode == True :
        print "  ", ip, alive, ping, pingfail, health, lastscan, reserved, result['_id']
    
    # set ping-loop iterator
    ploop = 1
    presult = 0

    # PING ALL OF THE THINGS 5 TIMES!!!!!
    while ploop < 6 :
        response = os.system("ping -W 100 -c 1 " + ip + " > /dev/null 2>&1")
        if response == 0:
            ping += 1
            presult += 1
        else:
            pingfail += 1
            ping += 1
        ploop += 1


    # set the time on the lastscan field
    lastscan = str(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

    # health status in %
    pct = (100 - int((float(pingfail)/float(ping))*100))
    health = pct

    # set alive & reservered flags
    if presult > 3 :
        alive = True
        lastalive = lastscan
        if imode == True :
            print bcolors.green + "   Host " + str(ip) + " passed. Health: " + str(health) + "%." + bcolors.ENDC
        if reserved == True :
            reserved = False
    else:
        alive = False
        if reserved == True :
            if imode == True :
                print bcolors.red + "   Host " + str(ip) + " is not up, keeping reservation." + bcolors.ENDC
        if reserved == False :
            if imode == True :
                print bcolors.red + "   Host " + str(ip) + " failed! Health: " + str(health) + "%." + bcolors.ENDC

    # check tidy flag and set flag if needed
    if pct < 11 :
        current_date = lastscan[6:10] + lastscan[0:2] + lastscan[3:5]
        last_alive = lastalive[6:10] + lastalive[0:2] + lastalive[3:5]
        diff = (int(current_date) - int(last_alive))
        if diff > config_keephosts :
            tidyflag = True
            if imode == True :
                diff = str(diff)
                print bcolors.red + "   Host " + str(ip) + " has been dead for " + diff[0:1] + " months, " + diff[1:3] + " days." 
                print "   Host will be removed on next cleanup." + bcolors.ENDC
    

    # save to DB
    coll.update( {"_id":result['_id'] } , { "$set": { "ipaddr": ip, "hostname": hostname, "user": user, "added": added, "alive": alive, "ping": ping, "pingfail": pingfail, "health": health, "lastscan": lastscan, "reserved": reserved, "tidyflag": tidyflag, "lastalive": lastalive, "login": login, "subnet": subnet, "vlan": vlan } } ) 

    # increment iterator 
    i += 1


# write to log @ start
f = open('/stv2/scripts/logfile','a')
f.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : Cambridge seccussfully scanned " + str(rows) + " hosts.\n")
f.close()

# Wait for user input in interactive mode.
if imode == True :  
    print ""
    var = raw_input(bcolors.green + "Scanning completed. Press <ENTER> to exit." + bcolors.ENDC)
    os.system("clear")

# END
