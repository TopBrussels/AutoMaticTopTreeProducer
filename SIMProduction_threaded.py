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
    Type=""
    Campaign=""
    CMSSW_sim=""
    GT_sim=""
    PublishName_sim=""
    CMSSW_rec=""
    GT_rec=""
    PublishName_rec=""
    CMSSW_top=""
    GT_top=""
    nEvents=""
    LHEDir=""
    Template=""
    
    DBSInst=""
    DBSsample=""

    Priority=int(0)

    doDry=bool(False)
    
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

        self.sql.createQuery("UPDATE","simrequests","","SET `Status` = 'Queued' WHERE `id` = "+str(self.ID)+" LIMIT 1")
        
        self.sql.execQuery()
        
    def setRunning(self):
            
        self.sql.createQuery("UPDATE","simrequests","","SET `Status` = 'Running' WHERE `id` = "+str(self.ID)+" LIMIT 1")
        
        self.sql.execQuery()

    def setDone(self):

        self.sql.createQuery("UPDATE","simrequests","","SET `Status` = 'Done', `Priority` = '0' WHERE `id` = "+str(self.ID)+" LIMIT 1")
       
        self.sql.execQuery()

    def invalidate(self):

        self.sql.createQuery("UPDATE","simrequests","","SET `Status` = 'Pending', `Priority` = '0' WHERE `id` = "+str(self.ID)+" LIMIT 1")

        self.sql.execQuery()

    def process(self):
        
        cmssw=""
        gt=""
        publish=""
        template=""
        LHEDir=""
        SKIPRECO=""

        DBS=""
        SAMPLE=""
        
        if not self.Type.rfind("GEN-SIM") == -1:
            template=" -f "+self.Template+" "
            LHEDir="-d "+self.LHEDir+" "
            if not self.Type.rfind("DIGI-RECO") == -1:
                cmssw=self.CMSSW_sim+","+self.CMSSW_rec
                gt=self.GT_sim+","+self.GT_rec
                publish=self.PublishName_sim+","+self.PublishName_rec 
            else:
                cmssw=self.CMSSW_sim
                gt=self.GT_sim
                publish=self.PublishName_sim
                SKIPRECO=" -s "
        else:
            cmssw=self.CMSSW_rec
            gt=self.GT_rec
            publish=self.PublishName_rec
            DBS=" --dbsInst "+self.DBSInst
            SAMPLE=" --start-from-produced-sim="+self.DBSsample+" "
            
        cmd ="python AutoMaticSIMProducer.py -c "+cmssw+" -g "+gt+" -p "+publish+" -a "+self.Campaign

        if not template == "":
            cmd+=template
        if not LHEDir == "":
            cmd+=LHEDir
        if not DBS=="":
            cmd+=DBS
        if not SAMPLE=="":
            cmd+=SAMPLE
        if not SKIPRECO=="":
            cmd+=SKIPRECO
    
        if not self.nEvents == "":
            cmd+=" -n "+self.nEvents

        if self.doDry:

            cmd+=" --dry-run "

        cmd += " --setLogFile logs/log-TopDB-SIMRequest-"+str(self.ID)+".txt"
        
        cmd += " >& logs/stdout"

        log.output(cmd)

        #print cmd

        #sys.exit(1)
        #return 0

        #print self.DBSsample.split("\n")
        #print SAMPLE.split("\n")
        #sys.exit(1)
         

        #cmd = "sleep 1"

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

        self.sql.createQuery("UPDATE","simrequests","","SET `Status` = 'Pending' WHERE `Status` = 'Queued'")
            
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

  
    def getDataSetProperties(self):
        
        self.sql.createQuery("SELECT","simrequests","*","Status = 'Pending' OR Status = 'Queued' ORDER BY `Priority` DESC")

        f = open("sql.out","w")
        f.write(self.sql.execQuery())
        f.close()
    
        for res in open("sql.out","r"):

            #print res
            
            line = res.split("\n")[0]
            sqlRes = line.split("	")

            for a in xrange(len(sqlRes)):
                sqlRes[a]=sqlRes[a].split("\n")[0]
                sqlRes[a]=sqlRes[a].split("\r")[0]
            
            if sqlRes[0].rfind("id") == -1:
                
                request = Request()
                
                request.ID = sqlRes[0]
                request.Type=sqlRes[3]
                request.Campaign=sqlRes[4]

                if not request.Type.rfind("GEN-SIM") == -1:
                    request.CMSSW_sim=sqlRes[5]
                    request.GT_sim=sqlRes[6]
                    request.nEvents=sqlRes[17]
                    request.LHEDir=sqlRes[16]
                    request.Template=sqlRes[7]
                    request.PublishName_sim=sqlRes[14]

                if not request.Type.rfind("DIGI-RECO") == -1:                        
                    request.CMSSW_rec=sqlRes[8]
                    request.GT_rec=sqlRes[9]

                    if request.Type.rfind("GEN-SIM") == -1:
                        request.DBSInst=sqlRes[10]
                        request.DBSsample=sqlRes[13]
                    

                request.CMSSW_top=""
                request.GT_top=""

                request.Priority = int(sqlRes[18])
            
                if not request.Priority == 0:

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

            if not request.Type == "":

                log.output("--> Starting production for request "+request.ID)

                request.setRunning()

                exitCode = request.process() # running AutoMaticSIMProducer
                    
                if exitCode == 0:

                    log.output("--> Production for request "+request.ID+" is finished, removing request from TopDB!")

                    request.setDone()

                elif exitCode == 1:

                    log.output(" ---> The script encountered a python error for request "+request.ID+", sending email to admins!")

                    request.invalidate()

                    # put all queued requests on hold again

                    request.resetQueue()
                    
                    # send email

                    sendErrorMail(exitCode,request.ID)

                    #sys.exit(1)

                elif exitCode == 2:

                    log.output(" ---> Something is wrong in the configuration for request "+request.ID+". Disabling this entry and sending a mail for manual intervention")

                    request.invalidate()
                    
                    # send email

                    sendErrorMail(exitCode,request.ID)

#############
## METHODS ##
#############


def sendErrorMail(exitCode,ID):

    global log
    global options

    cmd ='pwd'
    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    dir = pExe.stdout.read()
        
    log.output("********** SCRIPT GOT TERMINATE SIGNAL -> ALERTING PRODUCTION TEAM **********")
        
    mail = MailHandler()

    type = "error"

    subject = "Problem within the Simulation Workflow"

    msg = "Dear top quark group,\n"
    msg += "\n"
    msg += "This is an automatically generated e-mail to inform you that the production workflow encountered problems during the processing of request "+ID+"."
    msg += "\n\nReason:"
    if exitCode == 1:
        msg += "\n\n\t AutomaticSIMProducer exited with code 1 -> probabely a python exception. The workflow is now terminated. Please investigate and restart the workflow."
    if exitCode == 2:
        msg += "\n\n\t AutoMaticSIMProducer encountered a problem in the request configuration. This request is put inactive (Priority 0) until manual intervention."
    msg += "\n\nSTDOUT log: "+dir+"/"+"stdout"
    
    msg += "\n\n\nCheers,\nSIMProduction.py"

    #if not options.dryRun:
        #mail.sendMail(type,subject,msg)


def getnWorkers():

    for line in open(".config","r"):
        if not line.rfind("nWorkersSIM") == -1:
            return int(line.split(" ")[1].split("\n")[0])

    return int(0)

###################
## OPTION PARSER ##
###################

# Parse the options
optParser = OptionParser()

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
    log = logHandler("logs/SIMProductionWorkflow.txt")
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
