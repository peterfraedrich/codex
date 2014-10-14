#!/usr/bin/python
#
# magellan.py // db host auto-discovery
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
import socket

# set vars
recompile = False
added = 0
scanned = 0

# get CLI args
if len(sys.argv) > 1 :
    if sys.argv[1] == "-r" :
        recompile = True
    elif sys.argv[1] == "recompile" :
        recompile = True
    elif sys.argv[1] == "-h" :
        print """Magellan supports two modes: recompile and scan. To recompile the IP list, run with flag -r """
        sys.exit() 
    elif sys.argv[1] == "help" :
        print """Magellan supports two modes: recompile and scan. To recompile the IP list, run with flag -r  """
        sys.exit()
    else:
        print """Magellan supports two modes: recompile and scan. To recompile the IP list, run with flag -r  """
        sys.exit() 

# write to log @ start
f = open('/stv2/scripts/logfile','a')
f.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : Magellan started successfully.")
if recompile == True :
    f.write(" Starting in recompile mode.\n")
else :
    f.write("\n")
f.close()

######### import options from config file
optionfile = [line.strip() for line in open('/stv2/scripts/cambridge_conf')]
magellanfile = [line.strip() for line in open('/stv2/scripts/magellan_conf')]

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

# MongoDB connection
client = MongoClient(config_dburl)
db = client.stv2
coll = db.hosts

##### if -r flag set, go into recompile mode
if recompile == True :

    # write to log @ start
    f = open('/stv2/scripts/logfile','a')
    f.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : Magellan started re-compiling the scanlist.\n")
    f.close()

    # clear scanlist file
    scanlist = open('/stv2/scripts/resources/scanlist', 'w')
    scanlist.write("")
    scanlist.close()

    # load resources into mem as vars
    ip_24 = [line.strip() for line in open('/stv2/scripts/resources/1254')]
    ip_8 = [line.strip() for line in open('/stv2/scripts/resources/0255')]

    # get number of subnets
    subnets = len(magellanfile)
    nets = list()
    i = 1
    ipaddr = 0

    # load IP ranges into RAM
    while i < subnets:
        nets.append(magellanfile[i].split("/"))
        i += 1

    print nets

    # FUTURE DEV: make this flexible to use any subnet ever, not just the first 4 multiples of 8.
    for each in nets :
        # if subnet = 24, remove last octect of IP and append list of ip addresses to start IP and write to file
        if each[1] == "24" :
            each[0] = each[0].split(".")[0]+"." + each[0].split(".")[1] +"."+ each[0].split(".")[2]+"."
            for line in ip_24 :
                ipaddr = each[0] + str(line) + "\n"
                scanlist = open('/stv2/scripts/resources/scanlist', 'a')
                scanlist.write(ipaddr)
                scanlist.close()

        elif each[1] == "16" :
            # if subnet = 16, remove last 2 octets of IP and append list of ip addresses to start IP and write to file
            each[0] = each[0].split(".")[0]+"." + each[0].split(".")[1] +"."
            for line in ip_8 :
                for line2 in ip_24:
                    ipaddr = each[0] + line + "." + line2 + "\n"
                    scanlist = open('/stv2/scripts/resources/scanlist', 'a')
                    scanlist.write(ipaddr)
                    scanlist.close()

        elif each[1] == "8" :
            # if subnet = 8, remove last 3 octets of IP and append list of ip addresses to start IP and write to file
            each[0] = each[0].split(".")[0]+"."
            for line in ip_8 :
                for line2 in ip_8:
                    for line3 in ip_24:
                        ipaddr = each[0] + line + "." + line2 + "." + line3 + "\n"
                        scanlist = open('/stv2/scripts/resources/scanlist', 'a')
                        scanlist.write(ipaddr)
                        scanlist.close()

        elif each[1] == "32" :
            # if subnet = 32, wite IP to file
            scanlist = open('/stv2/scripts/resources/scanlist', 'a')
            scanlist.write(each[0] + "\n")
            scanlist.close()

        else:
            # write err to log
            f = open('/stv2/scripts/logfile','a')
            f.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : Magellan could not scan, invalid subnet. Check your magellan_conf file.\n")
            f.close()

    sys.exit()

# if -r not set, do the main function of the script
if recompile == False :
    
    # get the list of hosts to scan
    iplist = [line.strip() for line in open('/stv2/scripts/resources/scanlist')]

    # do the thing
    for each in iplist :
        # check if IP is in  DB
        exists = coll.find_one({"ipaddr": each})
        print each
        print exists
        try :
            #this is ugly, but its the only way it will work right
            if exists['ipaddr'] == each :
                scanned = scanned + 1
            
            elif exists['ipaddr'] == None :
                scanned = scanned + 1
        except :
                scanned = scanned + 1
                ping = 0
                pingfail = 0
                # set ping-loop iterator
                ploop = 1
                presult = 0

                # PING ALL OF THE THINGS 5 TIMES!!!!!
                while ploop < 6 :
                    ipaddr = each
                    print ipaddr
                    response = os.system("ping -w 1 -c 1 " + ipaddr + " > /dev/null 2>&1")
                    if response == 0:
                        ping += 1
                        presult += 1
                    else:
                        pingfail += 1
                        ping += 1
                    ploop += 1
                if presult > 3 :
                    alive = True
                    pct = (100 - int((float(pingfail)/float(ping))*100))
                    health = pct
                    try :
                        hostname_long = socket.gethostbyaddr(ipaddr)
                        hostname = hostname_long[0]
                    except :
                        hostname = ""
                    discovery_date = str(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
                    save_item = ({
                        "ipaddr": ipaddr,
                        "hostname": hostname,
                        "user": "system discovery",
                        "added": discovery_date,
                        "alive": "True",
                        "ping": ping,
                        "pingfail": pingfail,
                        "health": health,
                        "lastscan": discovery_date,
                        "reserved": "false",
                        "tidyflag": "false",
                        "lastalive": discovery_date,
                        "login": "unknown",
                        "subnet": "unknown",
                        "vlan": "10"
                        })
                    print save_item
                    coll.insert(save_item)
                    added = added + 1


    # write results to log
    f = open('/stv2/scripts/logfile','a')
    f.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : Magellan scanned " + str(scanned) + " IP's and added " + str(added) + " IP's.\n")
    f.close()

# END