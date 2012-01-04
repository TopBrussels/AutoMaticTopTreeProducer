## This script will automatically process any given dataset into a TopTree

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

# import logHandler
from logHandler import logHandler

# import mailHandler
from MailHandler import MailHandler

# import interface to topDB
from sqlHandler import SQLHandler

#############
## METHODS ##
#############

def reset():

    global ID
    global DataSet
    global DataTier
    global RunSelection
    global useLocalDBS
    global skipPAT
    global CMSSW_VER
    global GlobalTag
    global Priority
    global is31Xsample

    ID=int(0)
    DataSet = ""
    DataTier = ""
    RunSelection = ""
    useLocalDBS = ""
    skipPAT = ""
    CMSSW_VER = ""
    GlobalTag = ""
    is31Xsample = bool(False)

def getDataSetProperties():

    global sql
    global ID
    global DataSet
    global DataTier
    global RunSelection
    global useLocalDBS
    global skipPAT
    global CMSSW_VER
    global GlobalTag
    global Priority
    global is31Xsample
    
    sql.createQuery("SELECT","requests","*","1 ORDER BY `Priority` DESC LIMIT 0,1")

    f = open("sql.out","w")
    f.write(sql.execQuery())
    f.close()
    
    for res in open("sql.out","r"):
            
        line = res.split("\n")[0]
        sqlRes = line.split("	")
        if not sqlRes[1].rfind("/") == -1:
            ID = sqlRes[0]
            DataSet = sqlRes[1]
            DataTier = sqlRes[2]
            RunSelection = sqlRes[3]
	    useLocalDBS = sqlRes[4]
            skipPAT = sqlRes[5]
            CMSSW_VER = sqlRes[6]
            GlobalTag = sqlRes[7]
            Priority = int(sqlRes[8])
            
    if Priority == 0:

        reset()

    else:
        
        sql.createQuery("SELECT","datasets","CMSSWversion","name REGEXP '"+DataSet+"' LIMIT 0,1")

        f = open("sql2.out","w")
        f.write(sql.execQuery())
        f.close()
    
        for res in open("sql2.out","r"):

            if res.rfind("CMSSWversion") == -1 and not res == "\n":

                if not res.rfind("CMSSW_31X") == -1:
                    is31Xsample = True;
                
        os.remove("sql2.out")

    os.remove("sql.out")

def sendErrorMail(exitCode):

    global log
    global DataSet
    global options

    cmd ='pwd'
    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    dir = pExe.stdout.read()
        
    log.output("********** SCRIPT GOT TERMINATE SIGNAL -> ALERTING PRODUCTION TEAM **********")
        
    mail = MailHandler()

    type = "error"

    subject = "Problem within the TopTree ProductionWorkflow"

    msg = "Dear top quark production group,\n"
    msg += "\n"
    msg += "This is an automatically generated e-mail to inform you that the production workflow encountered problems during the processing of "+DataSet+"."
    msg += "\n\nReason:"
    if exitCode == 1:
        msg += "\n\n\t AutomaticTopTreeProducer exited with code 1 -> probabely a python exception. The workflow is now terminated. Please investigate and restart the workflow."
    if exitCode == 2:
        msg += "\n\n\t AutoMaticTopTreeProducer encountered a problem in the request configuration. This request is put inactive (Priority 0) until manual intervention."
    msg += "\n\nSTDOUT log: "+dir+"/"+"stdout"
    
    msg += "\n\n\nCheers,\nStartProduction.py"

    if not options.dryRun:
        mail.sendMail(type,subject,msg)        

###################
## OPTION PARSER ##
###################

# Parse the options
optParser = OptionParser()

optParser.add_option("","--pbs-submit", action="store_true", dest="doPBS",default=bool(False),
                     help="Submit CRAB jobs to localGrid (Your dataset should be at T2_BE_IIHE)", metavar="")

optParser.add_option("","--dry-run", action="store_true", dest="dryRun",default=bool(False),
                     help="Perform a Dry Run (e.g.: no real submission)", metavar="")

optParser.add_option("","--log-stdout", action="store_true", dest="stdout",default=bool(False),
                     help="Write output to stdout and not to logs/log-*.txt", metavar="")


(options, args) = optParser.parse_args()

#if options.cmssw_ver == None:
#    optParser.error("Please specify a CMSSW version.\n")

#################
## DEFINITIONS ##
#################

# get the sensitive information from config file

login=""
password=""
dbaseName=""
dbaseHost=""

for line in open(".config","r"):
    if not line.rfind("DBUser") == -1:
        login = line.split(" ")[1].split("\n")[0]
    elif not line.rfind("DBPass") == -1:
        password = line.split(" ")[1].split("\n")[0]
    elif not line.rfind("DBHost") == -1:
        dbaseHost = line.split(" ")[1].split("\n")[0]
    elif not line.rfind("DBName") == -1:
        dbaseName = line.split(" ")[1].split("\n")[0]

sql = SQLHandler(dbaseName,login,password,dbaseHost)

if not options.stdout == True:
    log = logHandler("logs/ProductionWorkflow.txt")
else:
    log = logHandler("")

sleepTime = int(300)

ID=int(0)
DataSet = ""
DataTier = ""
useLocalDBS = ""
RunSelection = ""
skipPAT = ""
CMSSW_VER = ""
GlobalTag = ""
Priority = int(0)

is31Xsample = bool(False)

#################
## MAIN METHOD ##
#################

endlessloop=bool(True)

while endlessloop:
    
    getDataSetProperties()

    if not DataSet == "":

        # processing request

        if not is31Xsample:
            log.output("--> Starting production for sample "+DataSet+" ("+CMSSW_VER+")")

        else:
            log.output("--> Starting production for sample "+DataSet+" ("+CMSSW_VER+" -> Adjusting for 31X sample)")
            
        sql.createQuery("UPDATE","requests","","SET `Status` = 'Running' WHERE `ID` = "+str(ID))

        if not options.dryRun:
            sql.execQuery()

        cmd ='python AutoMaticTopTreeProducer.py -c '+CMSSW_VER+' -g '+GlobalTag+' -d '+DataSet

        if skipPAT == "1":

            cmd += " --skip-pat"

        if DataTier == "PAT":

            cmd += " --start-from-pat"

        if options.doPBS:

            cmd += " --pbs-submit"

        if options.dryRun:

            cmd += " --dry-run"

        if is31Xsample:

            cmd += " --run31Xcompat"

        if options.stdout:

            cmd += " --log-stdout"

        else:
            cmd += ">& logs/stdout"

        #print cmd
        
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

        # wait until the process is terminated

        while pExe.poll() == None:

            pExe.poll()

            time.sleep(10)

        if options.stdout:
            log.output(pExe.stdout.read())

        exitCode = int(pExe.poll())
        #exitCode = 0
        # possible exit codes: 0 (everything went fine) 1 (python error, need to send email) 2 (script error, mail sent by AutoMaticTopTreeProducer.py)

        

        ## remove sample from requests database if exit code is 0

        if exitCode == 0:

            log.output(" ---> Production seems successfull, removing sample from requests DB.")

            sql.createQuery("UPDATE","requests","","SET `Status` = 'Done', `Priority` = '0' WHERE `ID` = "+str(ID))

            if not options.dryRun:
                sql.execQuery()
    
        # if exitCode = 2, it is probabely due to misconfiguration eg. datasetname typo wrong CMSSW etc. In this case we disable the dataset in requests DB and we send an email
        
        elif exitCode == 2:

            log.output(" ---> Something is wrong in the configuration for this production. Disabling this entry and sending a mail for manual intervention")

            # send email

            sendErrorMail(exitCode)

            sql.createQuery("UPDATE","requests","","SET `Priority` = '0' WHERE `ID` = "+str(ID)+" LIMIT 1")

            if not options.dryRun:

                sql.execQuery()

        # exitCode 1 means trouble! This can be due to python errors,... This means that it makes no sense to move to the next sample so we kill the production loop and send an email
        
        if exitCode == 1:

            log.output(" ---> The script encountered an unrecoverable error, sending email to admins and exiting!")

            # send email

            sendErrorMail(exitCode)

            endlessloop=bool(False)

            sql.createQuery("UPDATE","requests","","SET `Priority` = '0' WHERE `ID` = "+str(ID)+" LIMIT 1")

            if not options.dryRun:
                            
                sql.execQuery()

        if not exitCode == 0:

            sql.createQuery("UPDATE","requests","","SET `Status` = 'Pending' WHERE `ID` = "+str(ID))
            
            if not options.dryRun:
                            
                sql.execQuery()

        reset()

        #time.sleep(sleepTime)

    else:

        log.output("--> No requested samples in database, sleeping "+str(sleepTime)+"s")
        time.sleep(sleepTime)


