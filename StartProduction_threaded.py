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

# import packages for multi-threading

import Queue
import threading

####################
## Helper Classes ##
####################

class Request:

    ID=int(0)
    DataSet = ""
    DataTier = ""
    useLocalDBS = ""
    RunSelection = ""
    skipPAT = ""
    DontStorePat = ""
    CMSSW_VER = ""
    CMSSW_VER_SAMPLE = ""
    GlobalTag = ""
    Priority = int(0)
    FLFilterPath = int(-1)
    
    wantGenEvent = bool(False)

    def __init__(self):

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

        self.sql = SQLHandler(dbaseName,login,password,dbaseHost)

    def setQueued(self):

        if not self.DataSet == "":

            self.sql.createQuery("UPDATE","requests","","SET `Status` = 'Queued' WHERE `ID` = "+str(self.ID)+" LIMIT 1")
        
            self.sql.execQuery()
            
    def setRunning(self):

        if not self.DataSet == "":

            self.sql.createQuery("UPDATE","requests","","SET `Status` = 'Running' WHERE `ID` = "+str(self.ID)+" LIMIT 1")
        
            self.sql.execQuery()

    def setDone(self):

       if not self.DataSet == "":

           self.sql.createQuery("UPDATE","requests","","SET `Status` = 'Done', `Priority` = '0' WHERE `ID` = "+str(self.ID)+" LIMIT 1")
       
           self.sql.execQuery()

    def invalidate(self):

        if not self.DataSet == "":

            self.sql.createQuery("UPDATE","requests","","SET `Status` = 'Pending', `Priority` = '0' WHERE `ID` = "+str(self.ID)+" LIMIT 1")

            self.sql.execQuery()

    def process(self):

        #print self.RunSelection

        cmd ='python AutoMaticTopTreeProducer.py -c '+self.CMSSW_VER+' --cmssw_sample '+self.CMSSW_VER_SAMPLE+' -g '+self.GlobalTag+' -d '+self.DataSet
        
        if self.skipPAT == "1":

            cmd += " --skip-pat"

        if self.DontStorePat == "1":

            cmd += " --dont-store-pat"
            
        if self.DataTier == "PAT":

            cmd += " --start-from-pat"

        if self.DataTier == "PAT-MC":

            cmd += " --start-from-pat-mc"

        if options.doPBS:

            cmd += " --pbs-submit"

        if options.dryRun:

            cmd += " --dry-run"

        if self.wantGenEvent:

            cmd += " --addGenEvent"

        if int(self.FLFilterPath) > 0:

            cmd += " --flavourHistoryFilterPath="+str(self.FLFilterPath)

        if not self.useLocalDBS == "":

            cmd += " --dbsInst "+self.useLocalDBS

        if not self.DataSet.rfind("USER") == -1 and self.DataTier.rfind("PAT") == -1: # then we need a datatier

            cmd += " -t "+self.DataTier

        cmd += " --setLogFile logs/log-TopDB-Request-"+str(self.ID)+".txt"

        if not self.RunSelection == "NULL" and not self.RunSelection == "":

            cmd += " -r "+str(self.RunSelection)

        #if options.stdout:
        #    cmd += " --log-stdout"
        #else:
        cmd += " >& logs/stdout"

        log.output(cmd)

        #return 0

        #cmd = "sleep 10"

        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

        # wait until the process is terminated

        while pExe.poll() == None:

            pExe.poll()

            time.sleep(10)

        if options.stdout:
            log.output(pExe.stdout.read())

        exitCode = int(pExe.poll())

        # possible exit codes: 0 (everything went fine) 1 (python error, need to send email) 2 (script error, mail sent by AutoMaticTopTreeProducer.py)

        return exitCode

        #return 0
    
    def resetQueue(self):

        self.sql.createQuery("UPDATE","requests","","SET `Status` = 'Pending' WHERE `Status` = 'Queued'")
            
        self.sql.execQuery()


class RequestHandler:

    sleepTime = int(300)

    requests = []
        
    def __init__(self):

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

        self.sql = SQLHandler(dbaseName,login,password,dbaseHost)

        self.getDataSetProperties()

    def patParentID(self,name):

         self.sql.createQuery("SELECT","patuples","dataset_id","name REGEXP '"+name+"' LIMIT 0,1")

         f = open("sql2.out","w")
         f.write(self.sql.execQuery())
         f.close()

         lines = open("sql2.out","r").readlines()

         if len(lines) == 2:

             return int(lines[1])

         else:

             return -1

    def getDataSetProperties(self):
        
        self.sql.createQuery("SELECT","requests","*","Status = 'Pending' OR Status = 'Queued' ORDER BY `Priority` DESC")

        f = open("sql.out","w")
        f.write(self.sql.execQuery())
        f.close()
    
        for res in open("sql.out","r"):

            #print res
            
            line = res.split("\n")[0]
            sqlRes = line.split("	")

            if len(sqlRes) < 11:
                continue
            
            if not sqlRes[1].rfind("/") == -1:
                request = Request()
                
                request.ID = sqlRes[0]
                request.DataSet = sqlRes[1]
                request.DataTier = sqlRes[2]
                request.RunSelection = sqlRes[3]
                request.FLFilterPath = sqlRes[4]
                request.useLocalDBS = sqlRes[5]
                request.skipPAT = sqlRes[6]
                request.DontStorePat = sqlRes[7]
                request.CMSSW_VER = sqlRes[8]
                request.GlobalTag = sqlRes[9]
                request.Priority = int(sqlRes[10])
            
                if not request.Priority == 0:

                    # in case it is reco->toptree (+- using pat)
                    
                    self.sql.createQuery("SELECT","datasets","CMSSWversion,process","name REGEXP '"+request.DataSet+"' LIMIT 0,1")

                    f = open("sql2.out","w")
                    f.write(self.sql.execQuery())
                    f.close()
    
                    for res in open("sql2.out","r"):
                        
                        #print res

                        line = res.split("\n")[0]
                        sqlRes = line.split("	")

                        if not sqlRes[0] == "CMSSWversion":
                            
                            #print "Ver: "+sqlRes[0]
                            request.CMSSW_VER_SAMPLE = sqlRes[0];

                            if sqlRes[1] == "TTJets" or sqlRes[1] == "TTbar":
                                request.wantGenEvent = True;

                            #print sqlRes[0]
                            #print request.CMSSW_VER
                            
                    os.remove("sql2.out")

                    # in case we start from pat

                    dataset_id = self.patParentID(request.DataSet)

                    #print dataset_id

                    if not dataset_id == -1:

                        #print "going from PAT"
                        self.sql.createQuery("SELECT","datasets","CMSSWversion,process","id = '"+str(dataset_id)+"' LIMIT 0,1")

                        f = open("sql2.out","w")
                        f.write(self.sql.execQuery())
                        f.close()
    
                        for res in open("sql2.out","r"):

                            #print res
                            line = res.split("\n")[0]
                            sqlRes = line.split("	")

                            if not sqlRes[0] == "CMSSWversion":

                                request.CMSSW_VER_SAMPLE = sqlRes[0];

                                #print sqlRes[0]
                                #print request.CMSSW_VER

                                if sqlRes[1] == "TTJets" or sqlRes[1] == "TTbar":
                                    request.wantGenEvent = True;

                                if not sqlRes[1] == "Data": 
                                    request.DataTier = "PAT-MC"
                                    
                            
                        os.remove("sql2.out")

                    self.requests.append(request)

        os.remove("sql.out")

################################
## WORKER CLASS FOR THREADING ##
################################
        
class WorkFlow (threading.Thread ):

    def __init__(self, *args, **kwds):

        threading.Thread.__init__(self, *args, **kwds)
    
        self.keepAlive = bool(True)

    def stop (self):
        
        self.keepAlive = bool(False)


    def run (self):
        
        # our thread runs forever
        
        while True:

            if not self.keepAlive:

                break

            # get the request from the queue

            request = requestsPool.get()

            if not request.DataSet == "":

                log.output("--> Starting production for sample "+request.DataSet+" ("+request.CMSSW_VER+")")

                request.setRunning()

                exitCode = request.process() # running AutoMaticTopTreeProducer
                    
                if exitCode == 0:

                    log.output("--> Production for sample "+request.DataSet+" is finished, removing request from TopDB!")

                    request.setDone()

                elif exitCode == 1:

                    log.output(" ---> The script encountered an unrecoverable error with "+request.DataSet+", sending email to admins and exiting!")

                    request.invalidate()

                    # put all queued requests on hold again

                    request.resetQueue()
                    
                    # send email

                    sendErrorMail(exitCode,request.DataSet)

                    sys.exit(1)

                elif exitCode == 2:

                    log.output(" ---> Something is wrong in the configuration for the production of "+request.DataSet+". Disabling this entry and sending a mail for manual intervention")

                    request.invalidate()
                    
                    # send email

                    sendErrorMail(exitCode,request.DataSet)

#############
## METHODS ##
#############


def sendErrorMail(exitCode,DataSet):

    global log
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


def getnWorkers():

    for line in open(".config","r"):
        if not line.rfind("nWorkers") == -1:
            return int(line.split(" ")[1].split("\n")[0])

    return int(0)

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

if not options.stdout == True:
    log = logHandler("logs/ProductionWorkflow.txt")
else:
    log = logHandler("")

#################
## MAIN METHOD ##
#################
    
# Create our Queue to store requests:

requestsPool = Queue.Queue ( 0 )

# check the # of workers to start

nWorkers=getnWorkers()

log.output("-- Starting the workflow with "+str(nWorkers)+" workers --")

# start our X threads

workers = []
for x in xrange ( nWorkers ):
   workers.append(WorkFlow())
   workers[x].start()

# setup the request and fill the queue

while True:

    # check if we need to start/kill threads

    nWorkers = len(workers)

    targetnWorkers = getnWorkers()

    if nWorkers < targetnWorkers:

        log.output("-- Number of requested workers changed to "+str(targetnWorkers)+" -> adding "+str(targetnWorkers-nWorkers)+" workers --")

        for x in xrange ( targetnWorkers-nWorkers ):
            workers.append(WorkFlow())
            workers[len(workers)-1].start()
            time.sleep(5) # to make shure not more than 1 process uses sql

    if nWorkers > targetnWorkers:

        log.output("-- Number of requested workers changed to "+str(targetnWorkers)+" -> removing "+str(-targetnWorkers+nWorkers)+" workers --")

        for x in xrange ( nWorkers-targetnWorkers ):
            workers.pop(len(workers)-1).stop()

    nWorkers = len(workers)

    log.output("-- Worker status -> "+str(nWorkers)+" running --")

    # with 0 workers, there is no need to do anything....

    if nWorkers == 0:

        time.sleep(600)

        continue

    # check if there is a worker that died
    
    for worker in workers:

        #print worker

        if not worker.isAlive(): # if ANY of our workers died -> kill program

            log.output("--ERROR-- One of the workers died, exiting")
            #sys.exit(1)

    log.output("-> Polling TopDB");

    # empty the pool
    while not requestsPool.empty():

        requestsPool.get()
    
    req = RequestHandler()

    for i in req.requests:

        i.setQueued()

        #log.output(i.DataSet+" -> Priority: "+str(i.Priority))

        requestsPool.put(i)

        time.sleep(5) # to make shure not more than 1 process uses sql

    #while not requestsPool.empty():

    #    print requestsPool.get().DataSet

    del req.requests[:] # empty requests container
    
    time.sleep(1800)
