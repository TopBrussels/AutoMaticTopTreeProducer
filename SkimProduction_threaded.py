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

#################
## JSON HELPER ##
#################

def mergeJSON ( json1,json2 ):

    import simplejson as json
    import sys

    my_crab_json=file(json2,'r')
    my_crab_dict = json.load(my_crab_json)
    official_lumi_json=file(json1,'r')
    official_lumi_dict = json.load(official_lumi_json)
    
    # now get our json stuff

    # compare our json with the official json

    # store keywords for official json
    kw_official_json = []
    for k, v in official_lumi_dict.items():
        for lumis in v:
            #    print "k:", k, " v:", v, " lumis:", lumis
            if type(lumis) == type([]) and len(lumis) == 2:
                for i in range(lumis[0], lumis[1] + 1):
                    kw="%d_%d" % (int(k),int(i))
                    #        print kw
                    kw_official_json.append(kw)

    # cross-check them with ours and fill the final dict
    kw_final_json = []
    for k, v in my_crab_dict.items():
        for lumis in v:
            if type(lumis) == type([]) and len(lumis) == 2:
                for i in range(lumis[0], lumis[1] + 1):
                    kw="%d_%d" % (int(k),int(i))
                    if kw in kw_official_json:
                        kw_final_json.append(kw)

    final_json_string = "{"
    previous_run = -1
    previous_lumi = -1
    for k in kw_final_json:
        splitted = k.split("_")
        run = splitted[0]
        lumi = splitted[1]
        if len(lumi) > 0:
            if run != previous_run:
                if previous_run != -1:
                    final_json_string += str(previous_lumi) + "]], "
                final_json_string += "\"" + str(run) + "\": [["
                previous_run = run
                previous_lumi = -1
            if int(previous_lumi) != ( int(lumi) - 1 ):
                if previous_lumi != -1:
                    final_json_string += str(previous_lumi) + "], ["
                final_json_string += str(lumi) + ", "
            previous_lumi = lumi
        else:
            print "Possible problem: len(lumi) =", len(lumi)
            print "k =", k

    final_json_string += str(previous_lumi) + "]]}"

    return final_json_string

####################
## Helper Classes ##
####################

class Request:

    ID=int(0)

    Username = ""
    Email = ""
    GridProxy = ""
    SamplePath = ""
    SkimXML = ""
    JSON = ""
    WorkingDir = ""
    nThreads = int(0)
    nGroupFiles = int(0)
    publishName = ""
    announce = int(0)
    walltime = ""
    host = ""
    
    
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

        if not self.SamplePath == "":

            self.sql.createQuery("UPDATE","skimrequests","","SET `Status` = 'Queued' WHERE `ID` = "+str(self.ID)+" LIMIT 1")
        
            self.sql.execQuery()
            
    def setRunning(self):

        if not self.SamplePath == "":

            self.sql.createQuery("UPDATE","skimrequests","","SET `Status` = 'Running' WHERE `ID` = "+str(self.ID)+" LIMIT 1")
        
            self.sql.execQuery()

    def setDone(self):

       if not self.SamplePath == "":

           self.sql.createQuery("UPDATE","skimrequests","","SET `Status` = 'Done' WHERE `ID` = "+str(self.ID)+" LIMIT 1")
       
           self.sql.execQuery()

    def invalidate(self):

        if not self.SamplePath == "":

            self.sql.createQuery("UPDATE","skimrequests","","SET `Status` = 'Pending' WHERE `ID` = "+str(self.ID)+" LIMIT 1")

            self.sql.execQuery()

    def process(self):

        stamp = strftime("%d%m%Y_%H%M%S")

        TopSkimDir = Popen("echo $HOME", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip()+"/TopSkim/"
        #TopSkimDir = "/user/mmaes/AutoMaticTopTreeProducer-DEV/UserCode/mmaes/TopSkim/"

        #export VO_CMS_SW_DIR="/swmgrs/cmss/"
        #export SCRAM_ARCH="slc5_ia32_gcc434"
        #source $VO_CMS_SW_DIR/cmsset_default.sh
        #cd ../../TopSkim
        #python SkimTopTree.py --mtop-runmode --toptree_location=/pnfs/iihe/cms/store/user/dhondt/TToBLNu_TuneZ2_tW-channel_7TeV-madgraph/Fall10-START38_V12-v2/18112010_093940/TOPTREE -t CMSSW_38X_v1/TopBrussels/TopTreeProducer/ --skim_xml=skim_1291979767.xml -n 50 -j 1 --email=michael.maes@vub.ac.be >& logs/topskim-error.txt

        # get the JSON File if needed

        if not self.JSON == "":

            #print self.JSON.split(";")[0]

            #JSONDest = "/localgrid/dhondt/JSON_"+stamp+".txt"
            #JSONDest = "/localgrid/mmaes/OFFICIAL_JSON_"+stamp+".json"
            JSONDest = "/localgrid/dhondt/OFFICIAL_JSON_"+stamp+".json"

            #print JSONDest

            Popen("wget -O "+JSONDest+" "+self.JSON.split(";")[0], shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

        # store the skim XML

        SkimFile = "skim_"+stamp+".xml"
        
        xmlFile = open(TopSkimDir+SkimFile,"w")

        xmlFile.write(self.SkimXML)

        xmlFile.close()

        # store the CRAB report JSON XML
            
        if len(self.JSON.split(";")) == 2:
            
            JSONFile = "/localgrid/dhondt/MERGED_JSON"+stamp+".json"
            
            cJSONFile = open(JSONFile,"w")
            
            cJSONFile.write(mergeJSON(JSONDest,self.JSON.split(";")[1]))
            
            cJSONFile.close()
            
            
        # if we use a JSON we need to change useJSON and JSONFile in the skim XML
        if not self.JSON == "":

            self.SkimXML = ""
            
            for line in open(TopSkimDir+SkimFile):

                if line.rfind("useJSON") == -1:
                    self.SkimXML += line
                else:
                    splitline = line.split("useJSON")
                    self.SkimXML += splitline[0]+"useJSON=\"1\" JSONFile=\""+JSONFile+"\"/>\n"

            xmlFile = open(TopSkimDir+SkimFile,"w")
            
            xmlFile.write(self.SkimXML)

            xmlFile.close()
            
            #print self.SkimXML

        # store the grid proxy

        ProxyFile = "grid_proxy_"+strftime("%d%m%Y_%H%M%S")+".proxy"

        pFile = open(TopSkimDir+ProxyFile,"w")

        pFile.write(self.GridProxy)

        pFile.close()

        cmd = ""
        #cmd += "export VO_CMS_SW_DIR=\"/swmgrs/cmss/\";"
        #cmd += "export SCRAM_ARCH=\"slc5_ia32_gcc434\";"
        #cmd += "source $VO_CMS_SW_DIR/cmsset_default.sh;"
        cmd += "export X509_USER_PROXY=\""+TopSkimDir+ProxyFile+"\";"
        cmd += "cd "+TopSkimDir+";"

        cmd += "python SkimTopTree.py --srmcp --mtop-runmode --mtop-setuser="+self.Username+" --toptree_location="+self.SamplePath+" -t "+self.WorkingDir+" --skim_xml="+SkimFile+" -j "+str(self.nThreads)+" -n "+str(self.nGroupFiles)+" -w "+str(self.walltime)+" --email "+self.Email
        #cmd += "python SkimTopTree.py --mtop-runmode --mtop-setuser="+self.Username+" --toptree_location="+self.SamplePath+" --skim_xml="+SkimFile+" -n "+str(self.nThreads)+" -j "+str(self.nGroupFiles)+" --email "+self.Email

        if self.host == "PBS":
            cmd += " --use-pbs"
        if not self.publishName == "":
            cmd += " -p "+self.publishName
            if self.announce:
                cmd += " -a"
                
        #cmd += "voms-proxy-info"

        log.output(cmd)

        #sys.exit(1)

        #cmd = ""
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

        while pExe.poll() == None:

            pExe.poll()

            time.sleep(10)

        if options.stdout:
            log.output(pExe.stdout.read())

        exitCode = int(pExe.poll())


        # clean up

        try:
            #os.remove(TopSkimDir+ProxyFile)
            #os.remove(TopSkimDir+SkimFile)
            os.remove(JSONDest)
            os.remove(JSONFile)

        except:

            log.output("Error cleaning up")

        return exitCode
        
    def resetQueue(self):

        self.sql.createQuery("UPDATE","skimrequests","","SET `Status` = 'Pending' WHERE `Status` = 'Queued'")
            
        self.sql.execQuery()


class RequestHandler:

    sleepTime = int(30)

    requests = []
        
    def __init__(self,host):

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

        self.getDataSetProperties(host)

    def getDataSetProperties(self,host):
        
        self.sql.createQuery("SELECT","skimrequests","*","(Status = 'Pending' OR Status = 'Queued') AND host = '"+host+"'")

        sqlFile = "sql_"+strftime("%d%m%Y_%H%M%S")+".out"

        f = open(sqlFile,"w")
        f.write(self.sql.execQuery())
        f.close()
    
        for res in open(sqlFile,"r"):

            #print res
            line = res.split("\n")[0]
            sqlRes = line.split("	")

            if len(sqlRes) < 10:
                continue

            if sqlRes[0].rfind("ID") == -1:

                request = Request();
                
                request.ID = sqlRes[0]
                request.Username = sqlRes[1]
                request.Email = sqlRes[2]
                request.SamplePath = sqlRes[4]
                request.JSON = sqlRes[6]
                request.WorkingDir = sqlRes[7]
                request.nThreads = int(sqlRes[8])
                request.nGroupFiles = int(sqlRes[9])
                request.walltime = sqlRes[10]
                request.publishName = sqlRes[11]
                request.announce = int(sqlRes[12])
                request.host = sqlRes[13]

                #print request.ID+" "+request.SamplePath+" "+request.Username

                tmp = sqlRes[3].split('\r')

                for line in tmp:

                    line = line.strip("\n").lstrip('\n')

                    split = line.split("\\n")

                    if len(split) == 1:
                        request.GridProxy += split[0]+'\n'
                    else:
                        request.GridProxy += split[1]+'\n'

                tmp = sqlRes[5].split('\r')

                #print tmp[0].split("\\n")

                for line in tmp[0].split("\\n"):

                    #line = line.strip("\n").lstrip('\n')

                    #print line

                    split = line.split("\\n")

                    if len(split) == 1:
                        request.SkimXML += split[0]+'\n'
                    else:
                        request.SkimXML += split[1]+'\n'

                #print request.SkimXML
                self.requests.append(request)

                #sys.exit(1);
        os.remove(sqlFile)

################################
## WORKER CLASS FOR THREADING ##
################################
        
class WorkFlow (threading.Thread ):
    
    def __init__(self, *args, **kwds):

        threading.Thread.__init__(self, *args, **kwds)
    
        self.keepAlive = bool(True)

        self.host = ""
        
    def stop (self):
        
        self.keepAlive = bool(False)

    def sethost(self, host):

        self.host=host

    def run (self):
        
        # our thread runs forever
        
        while True:
            
            # get the request from the queue

            request = Request()

            if self.host == "mtop2":
                request = requestsPool.get()
            elif self.host == "PBS":
                request = requestsPoolPBS.get()
                
            if not request.SamplePath == "":

                log.output("--> Starting production for user "+request.Username+"\n\t-> Email: "+request.Email+"\n\t-> SampleID: "+request.ID+"\n\t-> Sample: "+request.SamplePath+"\n\t-> TopTreeProducer: "+request.WorkingDir+"\n\t-> Host: "+request.host+"\n\t-> Announce: "+str(request.announce)+"\n\t-> PublishName: "+request.publishName+"\n\t-> nThreads/nGroupedFiles: "+str(request.nThreads)+"/"+str(request.nGroupFiles))

                request.setRunning()

                exitCode = request.process() # running AutoMaticTopTreeProducer

                if exitCode == 0:

                    log.output("--> FINISHED production for user "+request.Username+"\n\t-> Email: "+request.Email+"\n\t-> SampleID: "+request.ID+"\n\t-> Sample: "+request.SamplePath+"\n\t-> TopTreeProducer: "+request.WorkingDir+"\n\t-> Host: "+request.host+"\n\t-> Announce: "+str(request.announce)+"\n\t-> PublishName: "+request.publishName+"\n\t-> nThreads/nGroupedFiles: "+str(request.nThreads)+"/"+str(request.nGroupFiles))

                    request.setDone()

                elif exitCode == 1:

                    log.output("!!!!!!!--> ERROR WITH production for user "+request.Username+"\n\t-> Email: "+request.Email+"\n\t-> Sample "+request.SamplePath+"\n\t-> TopTreeProducer: "+request.WorkingDir+"\n\t-> Host: "+request.host+"\n\t-> Announce: "+str(request.announce)+"\n\t-> PublishName: "+request.publishName+"\n\t-> nThreads/nGroupedFiles: "+str(request.nThreads)+"/"+str(request.nGroupFiles))

                    request.invalidate()

                
#############
## METHODS ##
#############


def sendErrorMail(exitCode,DataSet):

    global log
    global options

    cmd ='pwd'


def getnWorkers(host):

    for line in open(".config","r"):
        if host == "mtop2":
            if not line.rfind("nSkimWorkersLocal") == -1:
                return int(line.split(" ")[1].split("\n")[0])

        elif host == "PBS":
            if not line.rfind("nSkimWorkersPBS") == -1:
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
    log = logHandler("logs/SKIMProductionWorkflow.txt")
else:
    log = logHandler("")

#################
## MAIN METHOD ##
#################
    
# Create our Queue to store requests:

requestsPool = Queue.Queue ( 0 )
requestsPoolPBS = Queue.Queue ( 0 )

# check the # of workers to start

nWorkersLocal=getnWorkers("mtop2")
nWorkersPBS=getnWorkers("PBS")

log.output("-- Starting the workflow with "+str(nWorkersLocal)+" local workers and "+str(nWorkersPBS)+" workers for PBS running --")

# start our X threads

workers = []
workersPBS = []
for x in xrange ( nWorkersLocal ):
   workers.append(WorkFlow())
   workers[x].sethost("mtop2")
   workers[x].start()
for x in xrange ( nWorkersPBS ):
   workersPBS.append(WorkFlow()) 
   workersPBS[x].sethost("PBS")
   workersPBS[x].start()

# setup the request and fill the queue

while True:

    #########################
    ## LOCAL WORKERS SETUP ##
    #########################

    # check if we need to start/kill threads

    nWorkers = len(workers)
    nWorkersPBS = len(workersPBS)
    
    targetnWorkers = getnWorkers("mtop2")
    targetnWorkersPBS = getnWorkers("PBS")

    # LOCAL
    
    if nWorkers < targetnWorkers:
        
        log.output("-- Number of requested local workers changed to "+str(targetnWorkers)+" -> adding "+str(targetnWorkers-nWorkers)+" workers --")

        for x in xrange ( targetnWorkers-nWorkers ):
            workers.append(WorkFlow())
            workers[len(workers)-1].sethost("mtop2")
            workers[len(workers)-1].start()
            time.sleep(5) # to make shure not more than 1 process uses sql

    if nWorkers > targetnWorkers:

        log.output("-- Number of requested local workers changed to "+str(targetnWorkers)+" -> removing "+str(-targetnWorkers+nWorkers)+" workers --")
        
        for x in xrange ( nWorkers-targetnWorkers ):
            workers.pop(len(workers)-1).stop()

    # PBS
    
    if nWorkersPBS < targetnWorkersPBS:
        
        log.output("-- Number of requested PBS workers changed to "+str(targetnWorkersPBS)+" -> adding "+str(targetnWorkersPBS-nWorkersPBS)+" workers --")

        for x in xrange ( targetnWorkersPBS-nWorkersPBS ):
            workersPBS.append(WorkFlow())
            workersPBS[len(workersPBS)-1].sethost("PBS")
            workersPBS[len(workersPBS)-1].start()
            time.sleep(5) # to make shure not more than 1 process uses sql

    if nWorkersPBS > targetnWorkersPBS:

        log.output("-- Number of requested PBS workers changed to "+str(targetnWorkersPBS)+" -> removing "+str(-targetnWorkersPBS+nWorkersPBS)+" workers --")
        
        for x in xrange ( nWorkersPBS-targetnWorkersPBS ):
            workersPBS.pop(len(workersPBS)-1).stop()
            
    nWorkers = len(workers)
    nWorkersPBS = len(workersPBS)

    log.output("-- Workers status -> "+str(nWorkers)+" local workers and "+str(nWorkersPBS)+" workers for PBS running --")

    # with 0 workers, there is no need to do anything....

    if nWorkers == 0 and nWorkersPBS == 0:
    
        time.sleep(300)
    
        continue

    # check if there is a worker that died

    for worker in workers:
    
        #print worker
    
        if not worker.isAlive(): # if ANY of our workers died -> kill program
        
            log.output("--ERROR-- One of the workers died, exiting")
            #sys.exit(1)
        
    log.output("-> Polling TopDB");


    #############################
    ## SETUP THE REQUEST POOLS ##
    #############################
    
    # empty the pools
    
    while not requestsPool.empty():

        requestsPool.get()

    while not requestsPoolPBS.empty():

        requestsPoolPBS.get()

    # local
    req = RequestHandler("mtop2")

    for i in req.requests:
            
        i.setQueued()
        
        #log.output(i.DataSet+" -> Priority: "+str(i.Priority))
        
        requestsPool.put(i)
        
        time.sleep(600) # to make shure not more than 1 process uses sql and to make sure that the previous request finished compiling
        
    #while not requestsPool.empty():
    
    #    print requestsPool.get().DataSet
    
    del req.requests[:] # empty requests container

    # PBS
    reqPBS = RequestHandler("PBS")

    for i in reqPBS.requests:
            
        i.setQueued()
        
        #log.output(i.DataSet+" -> Priority: "+str(i.Priority))
        
        requestsPoolPBS.put(i)
        
        time.sleep(600) # to make shure not more than 1 process uses sql and to make sure that the previous request finished compiling
        
    #while not requestsPool.empty():
    
    #    print requestsPool.get().DataSet
    
    del reqPBS.requests[:] # empty requests container
    
    time.sleep(300)
