## This script will automatically babysit any given crab task

# for command line options
from optparse import OptionParser

# regular expressions
import re

# interacting with the os
import subprocess
from subprocess import Popen, PIPE, STDOUT

# working with time
import time
from time import strftime, gmtime
from datetime import datetime

# working with numbers
from math import sqrt

# import system to terminate process
import sys

# import pathname module
import os,os.path

# import CRAB handler
from CrabHandler import CRABHandler

# import logHandler
from logHandler import logHandler

################################


###################
## CONFIGURABLES ##
###################

timestamp = strftime("%d%m%Y_%H%M%S")

crabCfgName = ""

logFileName = "logs/"+timestamp+".txt"

###################
## OPTION PARSER ##
###################

# Parse the options
optParser = OptionParser()

optParser.add_option("-d", "--dir", dest="dir",
                  help="Specify the CMSSW working directory where your crab cfg is", metavar="")

optParser.add_option("", "--cfgname", dest="cfgname",
                  help="Specify the filename of your crab cfg (default: crab.cfg)", metavar="")

optParser.add_option("", "--attach", dest="attach",
                  help="Attach the babysitter to an existing task. Provide the directory name as argument", metavar="")

optParser.add_option("", "--publish", action="store_true", dest="doPublish", default=bool(False),
                  help="Use this bool to have crab publish your output to local DBS. NOTE: use only when using --attach, when starting with the crab.cfg, the script guesses from the config file", metavar="")

optParser.add_option("","--log-stdout", action="store_true", dest="stdout",default=bool(False),
                     help="Write output to stdout and not to logs/log-*.txt", metavar="")

optParser.add_option("", "--idleTime", dest="idleTime",default=int(300),
                  help="Specify the time between crab -status (default 300s)", metavar="")

optParser.add_option("", "--idleTimeResubmit", dest="idleTimeResubmit",default=int(60),
                  help="Specify the time to wait before crab -status after a job resubmission (default 60s)", metavar="")

(options, args) = optParser.parse_args()

if options.dir == None:
    optParser.error("Please specify a working directory!\n")

if options.cfgname == None:
    crabCfgName = "crab.cfg"
else:
    crabCfgName = options.cfgname

if options.doPublish and options.attach == None:
     optParser.error("Please use --publish only together with --attach!\n")
    


################
## LOG SYSTEM ##
################

## provide the desired logfile name to logHandler
## if you provide an empty string the output will be written on the stdOut

if not options.stdout:
    log = logHandler(logFileName)
else:
    log = logHandler("")


#################
## MAIN METHOD ##
#################

# create a CrabHandler
    
crab = CRABHandler(timestamp,options.dir,log)

# change idle time

crab.idleTime=float(options.idleTime)
crab.idleTimeResubmit=float(options.idleTimeResubmit)

# set the crab env

crab.crabSource = "source /etc/profile.d/set_globus_tcp_port_range.sh; export EDG_WL_LOCATION=/opt/edg "

# check GRID proxy

crab.checkGridProxy(0)
crab.checkCredentials(0)

# check setup

toCheck = ["scram","crab"]

for i in toCheck:
    log.output("--> Checking if you have "+i+" in your path")
    check = Popen("which "+i, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

    if not check.rfind("no "+i+" in") == -1:
        log.output(" ---> ERROR:  you don't have "+i+" in your path, did you read the twiki instructions?")

        if options.stdout:
            print "Fatal ERROR, script exiting"
        else:
            print "Fatal ERROR, script exiting. Please consult "+logFileName+" for more information"
        sys.exit(1)

if options.attach == None:
        
    # now prepare our crab cfg

    #print crabCfgName
    
    crab.parseCRABcfg(timestamp,options.dir,crabCfgName)
    
    # submit jobs
    
    crab.submitJobs()
    
    # check jobs

else:

    crab.doPublish = options.doPublish

    if options.doPublish:

        log.output("--> Publishing results of crab task to DBS")

    crab.baseDir = options.dir
    crab.UIWorkingDir = options.attach
    
crab.checkJobs()

# publish?

crab.publishDataSet()

# check the FJR

crab.checkFJR()
