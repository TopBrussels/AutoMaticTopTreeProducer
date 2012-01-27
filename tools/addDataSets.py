# python script to remove obsolete productions

# will only work from the central account ;-)

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

from logHandler import logHandler

import random

# import DNS parse
#from DBSQuery import DBSManager

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


###############
### METHODS ###
###############

def insertDataSet(user,inputDataSet,Process,XS,CMSSWversion,DataTier,Availibility,Recommended):

    # check if dataset exists, else we insert it
    
    addit=bool(True)
    
    sql.createQuery("SELECT","datasets","*","`name` REGEXP '"+inputDataSet+"'")
    
    f = open("sql.out","w")
    f.write(sql.execQuery())
    f.close()
    
    for res in open("sql.out","r"):    
        line = res.split("\n")[0]
        if not line.rfind("/") == -1:
            addit = bool(False)
            
    values = []
    values.append([])
    values[len(values)-1].append("Date")
    values[len(values)-1].append(datetime.date.today().strftime("%Y-%m-%d"))
    values.append([])
    values[len(values)-1].append("User")
    values[len(values)-1].append(user)
    values.append([])
    values[len(values)-1].append("name")
    values[len(values)-1].append(inputDataSet)
    values.append([])
    values[len(values)-1].append("process")
    values[len(values)-1].append(Process)
    values.append([])
    values[len(values)-1].append("XSection")
    values[len(values)-1].append(XS)
    values.append([])
    values[len(values)-1].append("recommended")
    values[len(values)-1].append(str(Recommended))
    values.append([])
    values[len(values)-1].append("DataTier")
    values[len(values)-1].append(str(DataTier))
    values.append([])
    values[len(values)-1].append("CMSSWversion")
    values[len(values)-1].append(CMSSWversion)
    values.append([])
    values[len(values)-1].append("Availibilty")
    values[len(values)-1].append(Availibility)
    
    if addit:
        
        sql.createQuery("INSERT INTO","datasets","",values)
        
        sql.execQuery()
        
    else: # we just update the record
        
        query = "SET "
        
        for i in range(0,len(values)):
            
            if len(values[i]) == 2:
                 
                if not i == len(values)-1:
                    query += "`"+str(values[i][0])+"`='"+str(values[i][1])+"', "
                    
                else:
                    query += "`"+str(values[i][0])+"`='"+str(values[i][1])+"'"
                    
        query += " LIMIT 1"
                    
        sql.createQuery("UPDATE","datasets","",query)
        sql.execQuery()
                     

def insertRequest(inputDataSet,CMSSWversion,GlobalTag,prio,dbsInst,dataTier):
            
    values = []
    values.append([])
    values[len(values)-1].append("DataSet")
    values[len(values)-1].append(inputDataSet)
    values.append([])
    values[len(values)-1].append("DataTier")
    values[len(values)-1].append(dataTier)
    values.append([])
    values[len(values)-1].append("useLocalDBS")
    values[len(values)-1].append(dbsInst)
    values.append([])
    values[len(values)-1].append("DontStorePat")
    values[len(values)-1].append("1")
    values.append([])
    values[len(values)-1].append("CMSSWVersion")
    values[len(values)-1].append(CMSSWversion)
    values.append([])
    values[len(values)-1].append("GlobalTag")
    values[len(values)-1].append(GlobalTag)
    values.append([])
    values[len(values)-1].append("Priority")
    values[len(values)-1].append(prio)
    values.append([])
    values[len(values)-1].append("Status")
    values[len(values)-1].append("Pending")
    
        
    sql.createQuery("INSERT INTO","requests","",values)
    
    sql.execQuery()
                     

#####################
### OPTION PARSER ###
#####################

optParser = OptionParser()

optParser.add_option("","--dataset_file", dest="file",default="None",
                     help="File containing dataset info", metavar="")

optParser.add_option("","--search_dbs", dest="searchDBS",default="None",
                     help="Get Dataset info from dbs (query comes as argument)", metavar="")

(options, args) = optParser.parse_args()

if options.file == "None" and options.searchDBS == "None":

    print "For the options look at python addDatSets.py -h"
    sys.exit(1)

############
### MAIN ###
############

if not options.file == "None":
    if os.path.exists(options.file):

        for line in open(options.file,"r"):

            if not line.rfind("#") == -1 or line.rfind(":") == -1:
                continue

            sample = (line.split("\n")[0]).split(":")            
            
	    #print sample
	    #print len(sample)
            if len(sample) > 7:

                dataset=sample[0]
                datatier=sample[1]
                process=sample[2]
                xsect=sample[3]
                CMSSW=sample[4]
                reqCMSSW=sample[5]
                reqTag=sample[6]+"::All"
                reqPrio=sample[7]

                reqDBSInst = ""
                if len(sample) > 8:
                    reqDBSInst = sample[8]
                    
                
                print "\nAdding sample "+dataset+" (dataTier: "+datatier+" process: "+process+", XS: "+xsect+" pb, CMSSW: "+CMSSW+", requestCMSSW: "+reqCMSSW+", GlobalTag: "+reqTag+", Priority: "+reqPrio+", dbsInstance: "+reqDBSInst+")\n"
                
                insertDataSet("TopTree Producer",dataset,process,xsect,CMSSW,datatier,"Produced","0")
                
                #ans = str(raw_input('\nDo you want to add a request? (y/n): '))
                ans = "y"
            
                if not ans == "n" and not ans == "y":

                    print "\n\nWrong answer given!!!!\n\n"
                
                    sys.exit(1)
                
                elif ans == "n":
                
                    print "\n\nNo actions where taken, killing this script\n\n"
    
                else:
                    
                    insertRequest(dataset,reqCMSSW,reqTag,reqPrio,reqDBSInst,datatier)


            else:

                sys.exit()


#if not options.searchDBS == "None":
    
#    dbsMgr = DBSManager();

#    list =  dbsMgr.getDataSets("find dataset where dataset="+options.searchDBS+" and dataset.status like VALID", summary="", begin=1, end="")

#    for i in xrange(len(list)):
#        print list[i][1]

