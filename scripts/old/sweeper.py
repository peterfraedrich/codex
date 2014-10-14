#!/usr/bin/python
#
# sweeper.py // db host auto-scanner
###########################
# ColdBlue USA
# Peter Christian Fraedrich
###########################
#
#

from pymongo import MongoClient
import sys
import os
import datetime
from datetime import datetime

# clean up logs
with open("/stv2/scripts/logfile") as l:
    lines = sum(1 for line in l)
if lines > 500 :
    cmd = "cp logfile logfile"+str(datetime.now().strftime("%m%d%Y-%H%M%S"))
    os.system(cmd)
    c = open('/stv2/scripts/logfile', 'w')
    c.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : Sweeper cleaned up the logs.")
    c.close

# write to log @ start
f = open('/stv2/scripts/logfile','a')
f.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : Sweeper started successfully.\n")
f.close()

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

# MongoDB connection
client = MongoClient(config_dburl)
db = client.stv2
coll = db.hosts

# blank out number of deleted records
number_deleted = 0

# get DB items with tidyflag
rows = coll.count()
i = 0

obj_id = list()

# iterate through db rows
while i < rows :

    # get row of db at index i
    result = coll.find()[i]

    # assign tidyflag to var
    flag = str(result['tidyflag'])

    # if flag is up, append to obj_id list
    if flag == "True" :
        obj_id.append(str(result['ipaddr']))
    elif flag == "true" :
        obj_id.append(str(result['ipaddr']))

    i += 1

# iterate through obj_id list and delete flagged hosts / deleting directly causes index errors in mongo
#for each in obj_id :
#    coll.remove({"ipaddr": each})
#    number_deleted = number_deleted + 1   
print obj_id

for each in obj_id :
    print 'ipaddr: ' + each + '\n'
    number_deleted = number_deleted + 1

# write to log @ end
f = open('/stv2/scripts/logfile','a')
if number_deleted == 0 :
    f.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : Sweeper had nothing to do.\n")
else:
    f.write(str(datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + " : Sweeper successfully cleaned up " + str(number_deleted) + " host records.\n")
f.close() 
