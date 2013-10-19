# script to update the json file in every toptree from a dataset that matches <search_strin>
# usage python updateJSONFile.py <search_string> <new_json_url>

# for command line options
from optparse import OptionParser

# regular expressions
import re

# interacting with the os
from subprocess import Popen, PIPE, STDOUT
import sys
import os, os.path

# time
import time, datetime

# sql interface
from sqlHandler import SQLHandler

# import crabhandler for proxy stuff

from CrabHandler import CRABHandler
from logHandler import logHandler

# get the sensitive information from config file

login=""
password=""
dbaseName=""
dbaseHost=""
        
for line in open("../.config","r"):
    if not line.rfind("DBUser") == -1:
        login = line.split(" ")[1].split("\n")[0]
    elif not line.rfind("DBPass") == -1:
        password = line.split(" ")[1].split("\n")[0]
    elif not line.rfind("DBHost") == -1:
        dbaseHost = line.split(" ")[1].split("\n")[0]
    elif not line.rfind("DBName") == -1:
        dbaseName = line.split(" ")[1].split("\n")[0]
        
sql = SQLHandler(dbaseName,login,password,dbaseHost)


#################
### MAIN LOOP ###
#################

if not len(sys.argv) >= 3:

    print "Usage: python updateJSONFile.py <search_string> <new_json_url>"

## get the datasets from TopDB containing <search_string>

print "\n-> Searching datasets in TopDB containing: "+sys.argv[1]
sql.createQuery("SELECT","datasets","id,name","name REGEXP '"+sys.argv[1]+"'")
 
result = sql.execQuery().split('\n')

if len(result) == 1:

    print "Error: no dataset was found matching: "+sys.argv[1]

    sys.exit(1)

for i in range(1,len(result)-1):

    id=result[i].split("\t")[0]
    dataset=result[i].split("\t")[1]

    print "\n  ---> Found matching dataset "+dataset

    print "\n   ----> Looking for associated TopTrees for which we can update the JSON"
    
    sql.createQuery("SELECT","toptrees","id,JSONFile,PUJSONFile","dataset_id LIKE '"+id+"'")
 
    result2 = sql.execQuery().split('\n')

    for i in range(1,len(result2)-1):

        tid = result2[i].split("\t")[0]
        old = result2[i].split("\t")[1]
        oldPU = result2[i].split("\t")[2]

        if not old == sys.argv[2]:

            ans=''
            if len(sys.argv) > 3:
                ans = str(raw_input('\n    -----> Update TopTree ID '+tid+' (Current: '+old+', PU: '+oldPU+') (y/n): ')) 
            else:
                ans = str(raw_input('\n    -----> Update TopTree ID '+tid+' (Current: '+old+') (y/n): '))
                
            if ans == "y":
            
                if len(sys.argv) > 3:
                    sql.createQuery("UPDATE","toptrees","","SET `PUJSONFile` = '"+sys.argv[3]+"' WHERE `id` = "+str(tid)+" LIMIT 1")
                    sql.execQuery()

                sql.createQuery("UPDATE","toptrees","","SET `JSONFile` = '"+sys.argv[2]+"' WHERE `id` = "+str(tid)+" LIMIT 1")

                sql.execQuery()

        else:

            print '\n    -----> TopTree ID '+tid+' already has the newest JSON file:  '+old
