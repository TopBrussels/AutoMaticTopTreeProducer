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
 
def insertSimRequest(campaign,CMSSWversion_sim,GlobalTag_sim,Template_sim,PublishName_sim,LHEList,nEvents,prio):

    global options
    
    values = []
    values.append([])
    values[len(values)-1].append("Date")
    values[len(values)-1].append(datetime.date.today().strftime("%Y-%m-%d"))
    values.append([])
    values[len(values)-1].append("User")
    values[len(values)-1].append(options.user)
    values.append([])
    
    values[len(values)-1].append("Campaign")
    values[len(values)-1].append(campaign)
    values.append([])
    values[len(values)-1].append("CMSSWver_sim")
    values[len(values)-1].append(CMSSWversion_sim)
    values.append([])
    values[len(values)-1].append("GlobalTag_sim")
    values[len(values)-1].append(GlobalTag_sim)
    values.append([])
    values[len(values)-1].append("Template_sim")
    values[len(values)-1].append(Template_sim)
    values.append([])
    values[len(values)-1].append("CMSSWver_top")
    values[len(values)-1].append("")
    values.append([])
    values[len(values)-1].append("GlobalTag_top")
    values[len(values)-1].append("")
    values.append([])
    values[len(values)-1].append("PublishName_sim")
    values[len(values)-1].append(PublishName_sim)
    values.append([])
    values[len(values)-1].append("LHEList")
    values[len(values)-1].append(LHEList)
    values.append([])
    values[len(values)-1].append("nEvents")
    values[len(values)-1].append(nEvents)
    values.append([])
    values[len(values)-1].append("Priority")
    values[len(values)-1].append(prio)
    values.append([])
    values[len(values)-1].append("Status")
    values[len(values)-1].append("Pending")
    
    #print values

    sql.createQuery("INSERT INTO","simrequests","",values)
    
    sql.execQuery()
 
                     

#####################
### OPTION PARSER ###
#####################

optParser = OptionParser()


optParser.add_option("-u","--user", dest="user",default="None",
                     help="Provide your TopDB username", metavar="")

optParser.add_option("","--simrequest_file", dest="file",default="None",
                     help="File containing dataset info", metavar="")


(options, args) = optParser.parse_args()

if options.file == "None" and options.searchDBS == "None":

    print "For the options look at python addDatSets.py -h"
    sys.exit(1)

if options.user == "None":

    print "Please provide your username using --user (-u) option"
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

                PublishName_sim=sample[0]
                LHEList=sample[1]
                nEvents=sample[2]
                campaign=sample[3]
                CMSSWversion_sim=sample[4]
                GlobalTag_sim=sample[5]+"::All"
                Template_sim=sample[6]
                prio=sample[7]
                   
                
                print "\nAdding simrequest (PublishName_sim: "+PublishName_sim+", LHEList: "+LHEList+", nEvents: "+nEvents+", campaign: "+campaign+", CMSSWversion_sim: "+CMSSWversion_sim+", GlobalTag_sim: "+GlobalTag_sim+", Template_sim: "+Template_sim+", prio: "+prio+")\n"
                
                insertSimRequest(campaign,CMSSWversion_sim,GlobalTag_sim,Template_sim,PublishName_sim,LHEList,nEvents,prio)
                
                #ans = str(raw_input('\nDo you want to add a request? (y/n): '))
                ans = "y"
            
                if not ans == "n" and not ans == "y":

                    print "\n\nWrong answer given!!!!\n\n"
                
                    sys.exit(1)
                
                elif ans == "n":
                
                    print "\n\nNo actions where taken, killing this script\n\n"
    
                #else:
                    
                    #insertRequest(dataset,reqCMSSW,reqTag,reqPrio,reqDBSInst,datatier,runsel)


            else:

                sys.exit()

