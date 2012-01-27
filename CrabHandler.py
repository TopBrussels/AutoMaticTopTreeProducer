# Class to handle crab things
#test of new CVS
import time
from time import strftime,gmtime
from datetime import datetime

# interacting with the os
from subprocess import Popen, PIPE, STDOUT

import sys

import os, os.path

import math

# for getting stuff from fjr files
from fjrHandler import FJRHandler,GreenBoxHandler
from xml.sax import make_parser

from xml.sax.handler import ContentHandler

# import our DBSHandler

from DBSHandler import DBSHandler

class CrabStatusParser(ContentHandler):
    
    # constructor
    def __init__ (self):

        self.maxResubmit = int(50)
        
        # is the current element one of the interesting ones
        self.isGoodElement = 0
        
        # record the value of interesting attributes
        self.nCreated=int(0)
        self.nReady=int(0)
        self.nWaiting=int(0)
        self.nSubmitting=int(0)
        self.nSubmitted=int(0)
        self.nScheduled=int(0)
        self.nRunning=int(0)
        self.nDone=int(0)
        self.nAborted=int(0)
        self.nFailed=int(0)
        self.nJobs=int(0)

        self.nJobsFailedToSubmit = int(0)

        self.submissionNumber=int(0)
        self.storage=""
        self.output = []
        
    # this is called for each element
    def startElement(self, name, attrs):
        
        if name == 'Job':

            self.isGoodElement = 1

            self.submissionNumber = attrs.get('submissionNumber')

        if name == 'RunningJob' and self.isGoodElement:

            state = attrs.get('statusScheduler')

            self.storage = attrs.get('storage')

            appExit = "0"
            wrapExit = "0"

            #print state

            #print attrs.get("jobId")
            
            if not str(attrs.get("applicationReturnCode")) == "None":
                appExit = attrs.get("applicationReturnCode")
            else:
                appExit="0"

            if not str(attrs.get("wrapperReturnCode")) == "None":
                wrapExit = attrs.get("wrapperReturnCode")
            else:
                wrapExit="0"

            if appExit == "":
                appExit = "0";
            if wrapExit == "":
                wrapExit = "0";
            
            self.output.append(attrs.get("jobId")+":"+str(self.submissionNumber)+":"+str(state)+":"+str(appExit)+":"+str(wrapExit)+":"+str(attrs.get("statusReason")))

            if state == "Created":
                self.nCreated += 1
            elif state == "Submitting":
                self.nSubmitting += 1
            elif state == "Submitted":
                self.nSubmitted += 1
            elif state == "Scheduled":
                self.nScheduled += 1
            elif state == "Ready":
                self.nReady += 1
            elif state == "Waiting":
                self.nWaiting += 1
            elif state == "Running":
                self.nRunning += 1
            elif state == "Done":
                if not int(appExit) == 0 or not int(wrapExit) == 0:
                    self.nFailed += 1
                else:
                    self.nDone += 1
            elif state == "Cleared" or state == "Retrieved":
                if not int(appExit) == 0 or not int(wrapExit) == 0:
                    self.nFailed += 1
                else:
                    self.nDone += 1
            elif state == "Aborted":
                self.nAborted += 1
            else:
                self.nAborted += 1
            

            self.nJobs += 1
            
    # this is called when an element is closed
    def endElement(self, name):
        # this is an attribute of some kind
        if name == 'Job' and self.isGoodElement:
            self.isGoodElement = 0

    def getStatus(self):

        return " ---> STATUS: Created: "+str(self.nCreated)+" Submitting: "+str(self.nSubmitting)+" Submitted: "+str(self.nSubmitted)+" Waiting: "+str(self.nWaiting)+" Ready: "+str(self.nReady)+" Scheduled: "+str(self.nScheduled)+" Running: "+str(self.nRunning)+" Done: "+str(self.nDone)+" Failed: "+str(self.nFailed)+" Aborted: "+str(self.nAborted)

    def getJobList(self):

        return self.output

    def getResubmitList(self):

        resubmit = ""

        #print self.output

        for i in xrange ( len (self.output) ):

            job = self.output[i]
            
            jobId = job.split(":")[0]
            nResubmits = job.split(":")[1]
            state = job.split(":")[2]
            appExitCode = job.split(":")[3]
            wrapExitCode = job.split(":")[4]
            statusReason = job.split(":")[5]

            if not state == "Created" and not state == "Submitting" and not state == "Submitted":

                if int(nResubmits) < self.maxResubmit and (int(appExitCode) > 0 or int(wrapExitCode) > 0):
                    resubmit += jobId+','

                if int(nResubmits) < self.maxResubmit and (not state.rfind("Cancelled") == -1 or not state.rfind("Aborted") == -1 or not state.rfind("CannotSubmit") == -1):
                    resubmit += jobId+','

                #if int(nResubmits) < self.maxResubmit and not statusReason.rfind("job exit code !=0") == -1:

                #    resubmit += jobId+','

            #elif int(nResubmits) >= self.maxResubmit:

            #    print  "Job "+jobId+" reached the maximum resubmission count"

        if resubmit == "":

            return "None"

        return resubmit[0:resubmit.rfind(',')]

    def getGetOutputList(self):

        getoutput = ""

        #print self.output

        for i in xrange ( len (self.output) ):

            job = self.output[i]
            
            jobId = job.split(":")[0]
            nResubmits = job.split(":")[1]
            state = job.split(":")[2]
            appExitCode = job.split(":")[3]
            wrapExitCode = job.split(":")[4] 

            if state == "Cleared" or state == "Done":

                if int(appExitCode) ==  0 and int(wrapExitCode) == 0:
                    
                    getoutput += jobId+','

        if getoutput == "":

            return "None"

        return getoutput[0:getoutput.rfind(',')]

#parser = make_parser()
#handler = CrabStatusParser()
#parser.setContentHandler(handler)
#parser.parse(open("/user/dhondt/AutoMaticTopTreeProducer/CMSSW_3_5_6_patch1_TopTreeProd_v10/src/ConfigurationFiles/WJets-madgraph/Summer09-MC_31X_V3_7TeV-v3/14042010_113732/PAT_Summer09-MC_31X_V3_7TeV-v3_14042010_113732/share/output.xml"))

#print handler.getStatus()
#print handler.getJobList()
            
class CRABHandler:

    def __init__ (self,time,base,logHandler):

        #** USER Settings

        self.myProxyServer = "myproxy.cern.ch"
        
        self.idleTime=int(3600)
        self.idleTimeResubmit=int(1800)
        self.maxResubmits=int(20)

        self.nEventsPerJob="50000"
        self.nEvents="-1"
        
        self.nEventsPerJob_server="10000"
        self.nEvents_server="-1"

        self.nMaxJobsPerSubmit=int(300)
        self.nJobsLeftToSubmit=int(0)
        self.submitInWaves = bool(False)

        self.forceWhiteList = bool(False)

        #** Do NOT touch

	self.serverName = ""
        self.nEventsChecked = int(0)

        self.log = logHandler

        self.dbsInst = "cms_dbs_prod_global"

        self.outputlocation=""

        self.taskname=""
        self.baseDir=base
        self.UIWorkingDir=""
        self.crabFileName=""
        self.timeStamp=time
        self.publishName=""
        self.doPublish=bool(False)   
        self.nResubmits=int(1)
        self.nJobsDone=int(0)
        self.nJobsAborted=int(0)
        self.nJobsCreated=int(0)

        self.nJobsFailedToSubmit=int(0)

        self.nJobsSucceededFJR=int(0)

        self.nEventsDBS=int(0)

        self.crabSource="" # empty for the current crab

        self.initEnv = 'cd '+self.baseDir+'; eval `scramv1 runtime -sh`; source /etc/profile.d/set_globus_tcp_port_range.sh;'

        # temp stuff

        self.noCrabStageOut = bool(False)

        self.doScriptExe = bool(False)

        self.AdditionalCrabInput = None

    def output(self,string):

        #print "\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+string
        self.log.output(string)

    def setForceWhiteList (self,force):

        self.output("--> CRABHandler: forceWhiteList was set to: "+str(force))

        self.forceWhiteList = force

    def getUserName(self):

        cmd ='echo $USER'
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()

        return out.split('\n')[0]

        #return "mmaes"
    
    def getVersion(self):

        cmd = self.initEnv+self.crabSource+'; crab -v'
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()

        return out.split('\n')[0]

    def createGridProxy(self):

        # get certificate password from config
        password=""
        for line in open(".config","r"):
            if not line.rfind("GridPass") == -1:
                password = line.split(" ")[1]
                
        cmd ='voms-proxy-init -voms cms:/cms/becms -valid 190:00 -pwstdin'
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                
        pExe.communicate(password)

    def genCredName(self,serverDN):

        import commands
        import traceback
        import time
        import re
        import logging

        try:
            from hashlib import sha1
        except:
            from sha import sha as sha1

        if len(serverDN.strip() ) > 0:
            return sha1(serverDN).hexdigest()

    def createMyProxyCredentials(self):

        self.createGridProxy()

        # first we create our credential on the myproxy server
        
        #cmd ='export GLOBUS_TCP_PORT_RANGE=20036,25000; myproxy-init --certfile=$X509_USER_PROXY --keyfile=$X509_USER_PROXY -d -n -s '+self.myProxyServer+' -x -t 168:00'
        cmd ='source /etc/profile.d/set_globus_tcp_port_range.sh; myproxy-init --certfile=$X509_USER_PROXY --keyfile=$X509_USER_PROXY -d -n -s '+self.myProxyServer+' -x -t 168:00'
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

        #print cmd

        # now we generate a credential for UCSD and CERN crabservers

        serverDNlist = []
        serverDNlist.append("/DC=ch/DC=cern/OU=computers/CN=vocms20.cern.ch")
        serverDNlist.append("/DC=ch/DC=cern/OU=computers/CN=vocms21.cern.ch")
        serverDNlist.append("/DC=ch/DC=cern/OU=computers/CN=vocms22.cern.ch")
        serverDNlist.append("/DC=org/DC=doegrids/OU=Services/CN=glidein-2.t2.ucsd.edu")
        serverDNlist.append("/DC=org/DC=doegrids/OU=Services/CN=submit-2.t2.ucsd.edu")
	serverDNlist.append("/C=IT/O=INFN/OU=Host/L=Bari/CN=crab1.ba.infn.it")
        serverDNlist.append("/DC=ch/DC=cern/OU=computers/CN=vocms58.cern.ch")
	serverDNlist.append("/C=DE/O=GermanGrid/OU=DESY/CN=host/t2-cms-cs0.desy.de")

        for serverDN in serverDNlist:

            cmd = 'myproxy-init --certfile=$X509_USER_PROXY --keyfile=$X509_USER_PROXY -d -n -s '+self.myProxyServer+' -x -R \''+serverDN+'\' -Z \''+serverDN+'\' -k '+self.genCredName(serverDN)+' -t 168:00'
            pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

            #print cmd
            #print pExe.stdout.read()

    def checkGridProxy (self,silent):

        if not silent:
            self.output("--> Checking GRID proxy")

        cmd = 'voms-proxy-info'
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.read()

        lines = output.split('\n')

        #print lines

        if lines[1] == "Couldn't find a valid proxy.":

            self.output(" ---> No Valid GRID proxy was retrieved, creating one.")

            #self.log.dieOnError("Job Submission: No valid GRID Proxy was retrieved, please create one!")

            self.createGridProxy()

        else:

            for i in xrange(len(lines)):

                if not lines[i].rfind("timeleft") == -1:

                    timeleft = lines[i].split("timeleft  : ")
                    
                    splittedtimeLeft = timeleft[1].split(":");
                    
                    if int(splittedtimeLeft[0]) < 110:
                        
                        self.output(" ---> Proxy validity is < 110h, renewing your proxy.")
                        
                        #self.log.dieOnError("Job Submission: Your proxy lifetime is below 10h, please renew it!")
                        
                        self.createGridProxy()
                        
                    else:
                        
                        if not silent:
                            self.output(" ---> Ok, valid proxy was found (Valid for "+str(timeleft[1])+")")

    def checkCredentials (self,silent):

        if not silent:
            self.output('--> Checking credentials on MyProxy server: '+self.myProxyServer)

        cmd = 'source /etc/profile.d/set_globus_tcp_port_range.sh; myproxy-info -d -s '+self.myProxyServer
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.read()
        
        lines = output.split('\n')
        
        #print lines
        
        if not lines[1].rfind("no credentials found for user") == -1:

            self.output(" ---> No Credentials are found on MyProxy Server "+self.myProxyServer+" , creating new credentials")

            self.createMyProxyCredentials()

        else:

            name = ""
            
            for i in xrange(len(lines)):

                if not lines[i].rfind("trusted retrieval policy: ") == -1:

                    name = lines[i].split("CN=")[1]
                    
                if not lines[i].rfind("timeleft") == -1:
                    
                    timeleft = lines[i].split("timeleft: ")
                    
                    splittedtimeLeft = timeleft[1].split(":")
                    
                    if int(splittedtimeLeft[0]) < 110:
                        
                        self.output(" ---> Credentials on MyProxy "+self.myProxyServer+" are valid < 110h, renewing credentials")

                        self.createMyProxyCredentials()
                        
                        break

                    else:

                        if not silent:
                            if not name == "":
                                self.output(" ---> Ok, valid Credential for server "+str(name)+" was found (Valid for "+str(timeleft[1])+")")
                            else:
                                self.output(" ---> Ok, valid Credential was found (Valid for "+str(timeleft[1])+")")

                            
    def checkCEstatus(self,CEname):

        self.output("--> Checking if CE "+CEname+" is ready to process our jobs")
        
        cmd = './tools/same/client/bin/same-query servicestatus serviceabbr=CE voname=cms servicestatusvo=cms nodename='+CEname
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.read() 

        print output

        if not output.rfind("ok") == -1:

            return bool(True)

        else:

            return bool(False)

    def checkCrabServers(self):

        # at this point we only consider the "GreenBox" CrabServers (UCSD and CERN)
        servers = []

        servers.append([])
        servers[len(servers)-1].append("CERN")
        servers[len(servers)-1].append("http://dlevans.web.cern.ch/dlevans/greenbox/CRABservers_CERNGLite.xml")
        
        servers.append([])
        servers[len(servers)-1].append("UCSD")
        servers[len(servers)-1].append("http://dlevans.web.cern.ch/dlevans/greenbox/CRABservers_UCSDGlideIn.xml")

        for i in xrange( len(servers) ):
            
            cmd ='curl -H \'Accept: text/xml\' '+servers[i][1]+' -o '+servers[i][0]+'.xml'

            pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            out = pExe.stdout.read()
        
            if os.path.exists(servers[i][0]+'.xml'):

                availability = 0
            
                try:

                    parser = make_parser()
                
                    handler = GreenBoxHandler()
                    parser.setContentHandler(handler)
                    parser.parse(open(servers[i][0]+'.xml'))
                
                    availability = handler.getAvailability()

                    #print servers[i][0]+' Crab Server Availability: '+str(availability)
                
                    if availability == 100:

                        os.remove(servers[i][0]+'.xml')

                        return servers[i][0]
            
                except:

                    os.remove(servers[i][0]+'.xml')

                    pass

        return "None"
        #return "bari"

    def setDBSInst(self,string):

        self.dbsInst = string

    def runTwoConfigs(self,conf1,conf2):

        self.output("--> Generating script_exe to run two CMSSW configs inside one CRAB job.")

        outFile = open(self.baseDir+"/rundouble.sh",'w')

        outFile.write("echo running config "+conf1+"\n")

        outFile.write("cmsRun pset.py\n")

        #outFile.write("echo python config "+conf2+"\n")

        #outFile.write("python "+conf2+"\n")

        outFile.write("echo running config expanded.py \n")

        outFile.write("cmsRun -e -j $RUNTIME_AREA/crab_fjr_$NJob.xml expanded.py \n")

        outFile.close()

        self.doScriptExe = bool(True)

        self.AdditionalCrabInput = "expanded.py"
        
    def createCRABcfg(self,CRABcfgFileName, dataSet, pSet, outputFile,type,publish,blackList,runSelection,forceStandAlone):

        #check if it's MC or data

        isData = False

        if not type == "GENSIM":

            if ((dataSet).split("/"))[3].rfind("GEN") == -1 and ((dataSet).split("/"))[3].rfind("SIM") == -1 and ((dataSet).split("/"))[3].rfind("USER") == -1:
                isData=True
            else:
        
                isData=False

        #self.nEventsChecked=1
        
	self.output("--> Generating CRAB configuration for "+str(pSet))

        if self.doScriptExe:

            self.output(" ---> Adding "+self.AdditionalCrabInput+" to the input sandbox")
            
        #self.crabSource = "export EDG_WL_LOCATION=/opt/edg; source /user/cmssoft/crab/latest/crab.sh"
        self.crabSource = "export EDG_WL_LOCATION=/opt/edg; source /jefmount_mnt/jefmount/cmss/CRAB/latest/crab.sh"
        
        self.serverName = "None"
        
        #self.serverName = self.checkCrabServers()
        # only possible at this moment for slc4 servers
        
        if type == "PAT" and not forceStandAlone:

            if self.nEventsChecked > 4999*int(self.nEventsPerJob_server) or self.nEventsChecked == 0: # if task > 400 jobs go with server

                self.serverName = "server"

        elif type == "TOPTREE" and not forceStandAlone:

            if self.nEventsChecked > 4999*int(self.nEventsPerJob) or self.nEventsChecked == 0: # if task > 400 jobs go with server

                self.nEventsPerJob_server = self.nEventsPerJob
                
                self.serverName = "server"

        elif int(self.nEvents) > 4999*int(self.nEventsPerJob):

            self.serverName = "server"

        if not self.serverName == "None":
            
            #self.crabSource = "	export EDG_WL_LOCATION=/opt/edg; source /user/cmssoft/crab/latest/crab.sh" # needed for crabserver
            
            self.output(" ---> Submitting trough CrabServer")
                
            if type == "PAT":
                self.nEventsPerJob = self.nEventsPerJob_server;
                self.nEvents = self.nEvents_server;

        else:

            self.output(" ---> Submitting jobs using stand-alone CRAB")

            if type == "PAT":
                self.nEventsPerJob = self.nEventsPerJob_server;
                self.nEvents = self.nEvents_server;

        dataSetSplit = dataSet.split("/");

        if not type == "GENSIM":
            self.UIWorkingDir = type+"_"+dataSetSplit[2]+"_"+self.timeStamp
            self.crabFileName = CRABcfgFileName

        else:
            self.UIWorkingDir = type+"_"+self.timeStamp
            self.crabFileName = CRABcfgFileName
            
    
        if publish:
            if type == "GENSIM":
                self.publishName=dataSet
            else:
                self.publishName = type+"_"+dataSetSplit[1]+'_'+dataSetSplit[2]+'_'+self.timeStamp
                
            self.doPublish=True


        if type == "GENSIM":
            dataSet="None"

        self.output(" ---> #events/job: "+self.nEventsPerJob)

	outFile = open(self.baseDir+"/"+CRABcfgFileName, 'w')
	
	outFile.write('[CRAB]\n')
	outFile.write('jobtype = cmssw\n')

        outFile.write('scheduler = glite\n')

        if not self.serverName == "None":
            outFile.write('use_server = 1\n\n')
        else:
            outFile.write('use_server = 0\n\n')
            
	outFile.write('[CMSSW]\n')
	outFile.write('datasetpath = '+dataSet+'\n')

        if self.dbsInst.rfind("global") == -1:
            outFile.write('dbs_url = https://cmsdbsprod.cern.ch:8443/'+self.dbsInst+'_writer/servlet/DBSServlet\n')
            
	outFile.write('pset = '+pSet+'\n')

        if not isData:
            outFile.write('events_per_job = '+self.nEventsPerJob+'\n')
            outFile.write('total_number_of_events = '+self.nEvents+'\n')

        else: # new since crab273 we have to split by lumi or by runs for data samples (not for MC)
            nJobsNominal = int(round(float(self.nEventsChecked)/float(self.nEventsPerJob)))+1
            outFile.write('number_of_jobs = '+str(nJobsNominal)+'\n')
            outFile.write('total_number_of_lumis = '+self.nEvents+'\n') # self.nEvents = -1 (except when debugging)

	outFile.write('output_file = ' + outputFile + '\n\n')
        if not runSelection == "":
            outFile.write('runselection = '+runSelection+'\n\n')

        # when we use script_exe we want to ignore the pooloutputmodules
        
        if self.doScriptExe:
            outFile.write('ignore_edm_output=1\n')
            
	outFile.write('[USER]\n')
	outFile.write('ui_working_dir = ' + self.UIWorkingDir + '\n')
	outFile.write('return_data = 0\n')
	outFile.write('copy_data = 1\n')
        outFile.write('storage_element = T2_BE_IIHE\n')

        if not publish:
            
            outFile.write('user_remote_dir = /'+dataSetSplit[1]+'/'+dataSetSplit[2]+'/'+self.timeStamp+"/"+type+'\n')

            self.outputlocation = '/pnfs/iihe/cms/store/user/'+self.getUserName()+'/'+dataSetSplit[1]+'/'+dataSetSplit[2]+'/'+self.timeStamp+"/"+type+'\n'

        if publish:
            outFile.write('publish_data = 1\n')
            outFile.write('publish_data_name = '+self.publishName+'\n')
            outFile.write('dbs_url_for_publication = https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet\n')

        outFile.write('check_user_remote_dir=0\n')
        outFile.write('xml_report = output.xml\n')

        # script exe stuff

        if self.doScriptExe:
            outFile.write('script_exe = rundouble.sh\n')
            outFile.write('additional_input_files = '+self.AdditionalCrabInput+'\n')
        elif not self.AdditionalCrabInput == None:
            outFile.write('additional_input_files = '+self.AdditionalCrabInput+'\n')
        
	outFile.write('[GRID]\n')
	outFile.write('rb = CERN\n')

        #if self.serverName == "None":
        outFile.write('dont_check_proxy =  1\n')

        #if not self.serverName == "None":
        outFile.write('proxy_server = '+self.myProxyServer+'\n')

	outFile.write('virtual_organization = cms\n')
	outFile.write('group = becms\n')
        if not blackList == "":
            outFile.write('ce_black_list = '+blackList+'\n')
	outFile.write('lcg_catalog_type = lfc\n')
	outFile.write('lfc_host = lfc-cms-test.cern.ch\n')
	outFile.write('lfc_home = /grid/cms\n')

        #if self.serverName == "None":
        #    outFile.write('additional_jdl_parameters = rank =-other.GlueCEStateEstimatedResponseTime;')
                
	
	outFile.close()

        #print self.outputlocation

    def createPBSCRABcfg(self,CRABcfgFileName, dataSet, pSet, outputFile,useLocalDBS):

        self.output("--> PBS Submission is currently decomissioned")

        sys.exit(1)

    def parseCRABcfg(self,timestamp, dir, crabcfg): # for crab babysitter

        self.baseDir = dir
        
        self.UIWorkingDir = "crab_"+timestamp

        #self.crabSource = "export EDG_WL_LOCATION=/opt/edg; source /user/cmssoft/crab/latest/crab.sh"

        self.output("--> Preparing CRAB configuration (removing white/black lists and setting ui_working_dir)")

        self.crabFileName = "CrabBabysit_"+timestamp+"_"+crabcfg

        out = []
        
        inFile = open(self.baseDir+"/"+crabcfg, 'r')
        outFile = open(self.baseDir+"/CrabBabysit_"+timestamp+"_"+crabcfg, 'w')

        for line in inFile:

            if line.rfind("ce_white") == -1 and line.rfind("ce_black") == -1:

                if line.rfind("ui_working_dir") == -1: 

                    out.append(line.strip())

                    if not line.rfind("[USER]") == -1:

                        out.append("ui_working_dir = "+self.UIWorkingDir+"\n")

                        out.append("xml_report = output.xml\n")

                    if not line.rfind("[GRID]") == -1:

                        out.append("dont_check_proxy =  1\n")

                    if not line.rfind("publish_data_name") == -1:

                        split = line.split("publish_data_name")[1]

                        split2 = split.split("=")[1]

                        if len(split2.split(" ")) > 1:
                        
                            self.publishName = split2.split(" ")[1]

                        else:

                            self.publishName = split2

                    if line.rfind("publish_data_name") == -1 and not line.rfind("publish_data") == -1 and not line.rfind("1") == -1:

                        self.doPublish = bool(True)

                        self.output(" ---> Publishing results as "+self.publishName)

        for line in out:

            outFile.write(line+"\n")

        inFile.close()
        outFile.close()

        # now set crabfilename to new config

    def scaleJobsSize(self,dataset,runselection,scalefactor):
     
	self.output("--> Checking number of events for "+dataset)

        split = runselection.split(',')
        runs = []
        if len(split) > 0 and not split[0] == "":

            self.output(" ---> Runselection applied: "+runselection)

            for run in split:

                runs.append(int(run))

        dbs = DBSHandler(self.dbsInst)
        
        nEventsDBS = dbs.getTotalEvents(dataset,runs)

        self.output(" ---> The sample contains "+str(nEventsDBS)+" events")

        self.nEventsChecked = nEventsDBS

        # now we might want to rescale our jobs

        if int(nEventsDBS)/int(self.nEventsPerJob) <= 600 and int(nEventsDBS)/int(self.nEventsPerJob) > 450:

            #print str(int(nEventsDBS)/int(self.nEventsPerJob))

            #print nEventsDBS
            #print self.nEventsPerJob
            self.nEventsPerJob_server = str(int(math.ceil(nEventsDBS/(450/scalefactor)))) # scale to ~450 jobs

            self.nEventsPerJob = str(int(math.ceil(nEventsDBS/(450/scalefactor)))) # scale to ~450 jobs

            self.output(" ---> Original <= 600 jobs so Changing #events/job to "+self.nEventsPerJob_server+" so we can use StandAlone CRAB (~450 jobs)")

            #sys.exit(1);

            return bool(False)
                    
        elif nEventsDBS > 5000000 and nEventsDBS < 10000000: # 5M < #events < 10M

            self.nEventsPerJob_server = str(int(math.ceil(nEventsDBS/(450/scalefactor)))) # scale to ~450 jobs

            self.nEventsPerJob = str(int(math.ceil(nEventsDBS/(450/scalefactor)))) # scale to ~450 jobs

            self.output(" ---> Changing #events/job to "+self.nEventsPerJob_server)

            return bool(True)

        elif nEventsDBS > 10000000: # events > 10M

            self.nEventsPerJob_server = str(20000*scalefactor)

            self.nEventsPerJob = str(20000*scalefactor)

            self.output(" ---> Changing #events/job to "+self.nEventsPerJob_server)

            return bool(True)

        else: # no need to rescale if # events < 5M

            self.output(" ---> Ok, leaving the # of events per job")
            
            return bool(False)

        return bool(False)

    def submitJobs(self):

        # get blacklisted sites from config
        blacklist=""
        for line in open(".config","r"):
            if not line.rfind("GridBlacklist") == -1:
                blacklist = line.split(" ")[1]

        whitelist=""
        if self.forceWhiteList:
            blacklist=""
            for line in open(".config","r"):
                if not line.rfind("GridWhitelist") == -1:
                    whitelist = line.split(" ")[1]

        nEventsDBS=int(0)
        nCreated=int(0)
        nSubmitted=int(0)

        #### CRAB -CREATE

        logFileName = "log_create_"+self.crabFileName

	self.output("--> Creating CRAB Jobs for "+self.UIWorkingDir+ " ("+self.getVersion()+")")

        cmd = self.initEnv+self.crabSource+'; crab -create -cfg ' + self.crabFileName+' -GRID.ce_black_list='+blacklist.strip()+' >& '+logFileName
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
	output = p.stdout.read()

        for line in open(self.baseDir+"/"+logFileName):
            if not line.rfind("Total of ") == -1 and not line.rfind("jobs created") == -1:
                             
                nCreated=int(line[line.index('Total of ')+9:line.rindex(' jobs')])

        #print nCreated
    
        ## CRAB -SUBMIT

        logFileName = "log_submit_"+self.crabFileName

	self.output("--> Submitting CRAB Jobs for "+self.UIWorkingDir+ " ("+self.getVersion()+")")

        # blacklist

        blackListLine = ""

        if not blacklist == "":
            self.output(" --> Submitting with blacklist: "+blacklist)
            blackListLine=' -GRID.ce_black_list='+blacklist.strip()

        # whitelist

        whiteListLine = ""

        if not whitelist == "":
            self.output(" --> Submitting with whitelist: "+whitelist)
            whiteListLine=' -GRID.ce_white_list='+whitelist.strip()


        submitLine = "-submit"
        if nCreated > self.nMaxJobsPerSubmit:
            self.submitInWaves=bool(True)
            self.output(" ---> Submitting this task in multiple batches, now submitting "+str(self.nMaxJobsPerSubmit)+"/"+str(nCreated)+" jobs.")
            self.nJobsLeftToSubmit=nCreated-self.nMaxJobsPerSubmit
            submitLine = "-submit "+str(self.nMaxJobsPerSubmit)
            

        cmd = self.initEnv+self.crabSource+"; crab "+submitLine+' -c '+self.UIWorkingDir+blackListLine+whiteListLine+' >& '+logFileName
        
	p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
	output = p.stdout.read()
	#print output
        
        for line in open(self.baseDir+"/"+logFileName):

            #print line

            #if not line.rfind("Total of ") == -1 and not line.rfind("jobs created") == -1:
                             
            #    nCreated=int(line[line.index('Total of ')+9:line.rindex(' jobs')])
                
            if not line.rfind("Total of ") == -1 and not line.rfind("jobs submitted") == -1:

                nSubmitted=int(line[line.index('Total of ')+9:line.rindex(' jobs')])

            if not line.rfind("can run on ") == -1 and not line.rfind("events") == -1:

                nEventsDBS=int(line[line.index('can run on ')+11:line.rindex(' events')])

            if self.UIWorkingDir == "crab_*" and not line.rfind("working directory") == -1: #if CRAB_2_2_1 we need to set this variable!

                self.UIWorkingDir = line[line.index('crab_'):line.rindex('/')]

        self.nJobsCreated=nCreated

        #self.output(" ---> According to DBS, the sample contains "+str(nEventsDBS)+" events.")

        if nCreated == 0:

            self.output(" ---> Problem creating CRAB jobs, please consult "+self.baseDir+"/"+logFileName)

            self.log.dieOnError("JOB Submission: Unable to create the crab jobs.")

        elif not self.submitInWaves and not nSubmitted == nCreated and nSubmitted > 0:

            self.output(" ---> Could not submit all created CRAB jobs ("+str(nSubmitted)+"/"+str(nCreated)+" started), please consult "+self.baseDir+"/"+logFileName)

            self.nJobsFailedToSubmit = nCreated-nSubmitted

            print self.nJobsFailedToSubmit

        if nCreated > 0 and nSubmitted == 0:

            self.output(" ---> Unable to submit any of the "+str(nCreated)+" created CRAB jobs, please consult "+self.baseDir+"/"+logFileName)

            self.log.dieOnError("JOB Submission: Unable to submit the crab jobs.")

        else:

            self.output(" ---> OK, submitted "+str(nSubmitted)+"/"+str(nCreated)+" crab jobs")

        self.nEventsDBS = self.nEventsChecked

    def checkJobs(self):

        blacklistCMD = ""
        whitelistCMD = ""

        srm = "srm://maite.iihe.ac.be:8443"

        firstPoll=bool(True)

        self.output("--> Checking jobs in "+self.UIWorkingDir+" every "+str(self.idleTime)+"s")

        done=bool(False)
          
        while not done:

            # check if an abort is requested

            #print self.baseDir+"/"+self.UIWorkingDir+"/.abort"

            if os.path.isfile(self.baseDir+"/"+self.UIWorkingDir+"/.abort"):

                self.output(" ---> CRAB abort requested in "+self.UIWorkingDir+", killing all running jobs that remain!")

                cmd = self.initEnv+self.crabSource+';crab -kill all -c '+self.UIWorkingDir
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                output = p.stdout.read()

                #print output

                done = bool(True)

                break

            # if no abort, just continue checking the jobs

            # make shure our grid proxy + crabserver creds are ok

            self.checkGridProxy(True) # make it silent to not have massive logfiles
            self.checkCredentials(True)
            
            cmd = self.initEnv+self.crabSource+';crab -status -c '+self.UIWorkingDir+' -USER.xml_report=output.xml >& crab.status'
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            output = p.stdout.read()

            parser = make_parser()
            handler = CrabStatusParser()
            parser.setContentHandler(handler)
            parser.parse(open(self.baseDir+"/"+self.UIWorkingDir+"/share/output.xml"))

            self.output(handler.getStatus())

            #print handler.getJobList()

            if not handler.getGetOutputList() == "None" and not self.submitInWaves:

                self.output("  ----> Retrieving crab output for finished jobs: "+handler.getGetOutputList())
                    
                cmd = self.initEnv+self.crabSource+'; crab -get '+handler.getGetOutputList()+' -c '+self.UIWorkingDir
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                output = p.stdout.read()
                #print cmd
                #print output

                if self.serverName == "None": # if standalone we need to check the status again after get

                    cmd = self.initEnv+self.crabSource+';crab -status -c '+self.UIWorkingDir+' -USER.xml_report=output.xml'
                    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    output = p.stdout.read()
            
                    parser.parse(open(self.baseDir+"/"+self.UIWorkingDir+"/share/output.xml"))

            #print self.nJobsFailedToSubmit

            #print handler.nCreated

            #print self.nJobsCreated
            
            if not handler.getResubmitList() == "None":

                blacklist = ""
                whitelist = ""

                self.output("  ----> Resubmitting aborted jobs: "+handler.getResubmitList())

                # get blacklisted sites from config
                blacklistConfig=""
                for line in open(".config","r"):
                    if not line.rfind("GridBlacklist") == -1:
                        blacklistConfig = line.split(" ")[1]

                # get whitelisted sites from config
                whitelistConfig=""
                if self.forceWhiteList:
                    blacklistConfig=""
                    for line in open(".config","r"):
                        if not line.rfind("GridWhitelist") == -1:
                            whitelistConfig = line.split(" ")[1]


                if not blacklistConfig == "":

                    self.output("   -----> Applying Global blacklist from config: "+blacklistConfig.strip())

                    blacklist = blacklistConfig.strip()

                if os.path.isfile(self.baseDir+"/"+self.UIWorkingDir+"/.blacklist"):

                    file = open(self.baseDir+"/"+self.UIWorkingDir+"/.blacklist","r")

                    lines = file.readlines()

                    if len(lines) > 0:

                        self.output("   -----> Applying on-the-fly blacklist: "+lines[0].strip())

                        if not blacklistConfig == "":
                            blacklist = blacklist+","+lines[0].strip()
                        else:
                            blacklist = lines[0].strip()                             

                    file.close()

                if not blacklist == "":
                    blacklistCMD = "-GRID.ce_black_list="+blacklist
                else:
                    blacklistCMD = ""

                if not whitelistConfig == "":

                    self.output("   -----> Applying Global whitelist from config: "+whitelistConfig.strip())

                    whitelist = whitelistConfig.strip()

                if not whitelist == "":
                    whitelistCMD = "-GRID.ce_white_list="+whitelist
                else:
                    whitelistCMD = ""
                

                # FIRST REMOVE POSSIBLE STAGEOUT FROM PREVIOUS SUBMITS OF THE SAME JOB
                
                cmd = 'srmls '+srm+'/'+self.outputlocation.strip()
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                out = pExe.stdout.read()
                
                #fileList = open("files_"+self.timeStamp+".txt","w")
                
                stamp = strftime("%d%m%Y_%H%M%S")
                outfile = open(stamp+"_out.txt","w")
                outfile.write(out)
                outfile.close()
                
                for i in (handler.getResubmitList()).split(','):
                    
                    self.output("   -----> Checking for obsolete files for job "+str(i)+" on pnfs ("+self.outputlocation.strip()+")")
                    
                    
                    try:
                        for line in open(stamp+"_out.txt","r"):
                            
                            if not line.rfind("TOPTREE_"+str(i)+"_") == -1 or not line.rfind("PAT_"+str(i)+"_") == -1:
                                
                                file = 'pnfs'+line.split('pnfs')[1]
                                
                                self.output("    ------> Removing file "+str(file))
                                
                                rmcmd = 'srmrm '+srm+'/'+file
                                rmpExe = Popen(rmcmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                                rmout = rmpExe.stdout.read()
                                
                            #print rmout
                            
                            os.remove(stamp+"_out.txt")
                    except:
                        a = "b"
                        #self.output("    ------> Unable to check pnfs for obsolete files")

                cmd = self.initEnv+self.crabSource+'; crab -forceResubmit '+handler.getResubmitList()+' '+blacklistCMD+' '+whitelistCMD+' -c '+self.UIWorkingDir
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                output = p.stdout.read()

                #print cmd                
                #print output

                self.output("  ----> Jobs resubmitted, sleeping "+str(self.idleTimeResubmit)+"s.")

                time.sleep(self.idleTimeResubmit)

                
                #self.nResubmits=self.nResubmits+1

            elif not handler.nCreated > self.nJobsCreated and handler.nCreated > self.nJobsFailedToSubmit and self.serverName == "None" and not self.submitInWaves:

                self.output("  ----> Resubmitting jobs that are stuck in created state.")

                cmd = self.initEnv+self.crabSource+'; crab -submit '+blacklistCMD+' -c '+self.UIWorkingDir
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                output = p.stdout.read()
    
            elif (handler.nCreated == 0 or handler.nCreated == self.nJobsFailedToSubmit) and handler.nReady == 0 and handler.nSubmitting == 0 and handler.nSubmitted == 0 and handler.nWaiting == 0 and handler.nScheduled == 0 and handler.nRunning == 0 and not firstPoll:

                self.nJobsDone = handler.nDone

                self.nJobsAborted = handler.nAborted

                if not self.nResubmits == 0 and handler.nAborted > 0:

                    self.output(" ---> All jobs finished but some where marked ABORTED.")

                elif handler.nAborted == 0:

                    self.output(" ---> All jobs reached DONE status")

                self.output("--> End of CRAB run for "+self.UIWorkingDir)

                done=True

            elif not firstPoll and self.nJobsLeftToSubmit > 0:

                blacklist = ""
                self.output("  ----> Batch submission: Submitting remaining jobs")

                # get blacklisted sites from config
                blacklistConfig=""
                for line in open(".config","r"):
                    if not line.rfind("GridBlacklist") == -1:
                        blacklistConfig = line.split(" ")[1]

                if not blacklistConfig == "":

                    self.output("   -----> Batch submission: Applying Global blacklist from config: "+blacklistConfig.strip())

                    blacklist = blacklistConfig.strip()

                if os.path.isfile(self.baseDir+"/"+self.UIWorkingDir+"/.blacklist"):

                    file = open(self.baseDir+"/"+self.UIWorkingDir+"/.blacklist","r")

                    lines = file.readlines()

                    if len(lines) > 0:

                        self.output("   -----> Batch submission: Applying on-the-fly blacklist: "+lines[0].strip())

                        if not blacklistConfig == "":
                            blacklist = blacklist+","+lines[0].strip()
                        else:
                            blacklist = lines[0].strip()                             

                    file.close()

                if not blacklist == "":
                    blacklistCMD = "-GRID.ce_black_list="+blacklist
                else:
                    blacklistCMD = ""

                logFileName = "log_submit_"+self.crabFileName

                submitLine=""
                if self.nJobsLeftToSubmit > self.nMaxJobsPerSubmit:
                    self.output("   -----> Batch submission: Submitting the next batch of jobs")
                    submitLine="-submit "+str(self.nMaxJobsPerSubmit)
                    self.nJobsLeftToSubmit = self.nJobsLeftToSubmit-self.nMaxJobsPerSubmit
                else:
                    self.output("   -----> Batch submission: Submitting the last batch of jobs")
                    submitLine="-submit "+str(self.nJobsLeftToSubmit)
                    self.nJobsLeftToSubmit = 0
                    self.submitInWaves=bool(False)
                    
                cmd = self.initEnv+self.crabSource+"; crab "+submitLine+' -c '+self.UIWorkingDir+" "+blacklistCMD+' >& '+logFileName
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                output = p.stdout.read()

                

                time.sleep(self.idleTime)

            else:

                firstPoll=bool(False)

                time.sleep(self.idleTime)

    def publishDataSet(self):

        dir = self.baseDir+"/"+self.UIWorkingDir+"/res"

        if self.doPublish:

            logFileName = "log_getoutput_"+self.crabFileName

            self.output("--> Retrieving crab output for "+self.UIWorkingDir)
            
            cmd = self.initEnv+self.crabSource+'; crab -getoutput  -c '+self.UIWorkingDir+' >& '+logFileName
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            output = p.stdout.read()

            cmdrenew = self.initEnv+self.crabSource+'; crab -renewCredential  -c '+self.UIWorkingDir+' >& renewCred_'+logFileName
            prenew = Popen(cmdrenew, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            #output = p.stdout.read()

            self.output("--> Publishing results to DBS for "+self.UIWorkingDir)

            logFileName = "log_publish_"+self.crabFileName
        
            cmd = self.initEnv+self.crabSource+'; crab -publish  -c '+self.UIWorkingDir+' >& '+logFileName
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            output = p.stdout.read()

            newdataset=""
            
            for line in open(self.baseDir+"/"+logFileName):

                if not line.rfind("=== dataset /") == -1:

                    newdataset = line.split("=== dataset ")[1]

            self.output("--> Published dataset as "+newdataset)

            self.publishName = newdataset

            return newdataset
        
        else:

            logFileName = "log_getoutput_"+self.crabFileName

            self.output("--> Retrieving crab output for "+self.UIWorkingDir)
            
            cmd = self.initEnv+self.crabSource+'; crab -getoutput  -c '+self.UIWorkingDir+' >& '+logFileName
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            output = p.stdout.read()

            cmdrenew = self.initEnv+self.crabSource+'; crab -renewCredential  -c '+self.UIWorkingDir+' >& renewCred_'+logFileName
            prenew = Popen(cmdrenew, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

            return str("Null")

    def getCrabJSON(self):

        dir = self.baseDir+"/"+self.UIWorkingDir+"/res"

        logFileName = "log_report_"+self.crabFileName

        self.output("--> Creating crab JSON report for "+self.UIWorkingDir)
        
        cmd = self.initEnv+self.crabSource+'; crab -report  -c '+self.UIWorkingDir+' >& '+logFileName
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.read()

        
        jsonFile = dir+"/"+"lumiSummary.json"

        if os.path.exists(jsonFile):
            return open(jsonFile).readlines()[0]

        return "No JSON report retrieved from CRAB"
    
    def checkFJR(self):

        self.output("--> Checking the FrameWorkJobReport in "+self.UIWorkingDir)

        nFailedJobs=int(0)

        nGoodJobs=int(0)

        total=int(0)

        parser = make_parser()

        dir = self.baseDir+"/"+self.UIWorkingDir+"/res"

        #dir = "/user/mmaes/AutoMaticTopTreeProducer-DEV/UserCode/mmaes/AutoMaticTopTreeProducer/CMSSW_3_3_6_patch6/src/ConfigurationFiles/TTbar/mmaes-PAT_TTbar_Summer09-MC_31X_V9_Feb15-v1_11032010_105235-7c4071db814d24e51e1b245b259a972c/11032010_141901/TOPTREE_mmaes-PAT_TTbar_Summer09-MC_31X_V9_Feb15-v1_11032010_105235-7c4071db814d24e51e1b245b259a972c_11032010_141901/res"

        for file in os.listdir(dir):

            if not file.rfind("fjr") == -1 and file.endswith(".xml"):

                #print file

                try:
                    handler = FJRHandler()
                    parser.setContentHandler(handler)
                    parser.parse(open(dir+"/"+file))

                    #print handler.getEventsProcessed()

                    if int(handler.getFrameworkExitCode()) != 0:
                        nFailedJobs=nFailedJobs+1
                        #self.log.analyseFJR(file,"CMSSW"+(file.split(".xml")[0]).split("crab_fjr_")[1]+".stdout")

                    else:

                        total = total+int(handler.getEventsProcessed())

                        #self.output("tmp info: exitcode "+handler.getFrameworkExitCode())

                        nGoodJobs=nGoodJobs+1

                except:

                    nFailedJobs=nFailedJobs+1

                    pass

        if not nFailedJobs == 0:
            self.output(" ---> Looking at the FJR, "+str(nFailedJobs)+" jobs are marked DONE but failed!")
        else:
            self.output(" ---> Looking at the FJR, all jobs seem to be successfull!")

        if total == 0:

            self.output(" ---> NO jobs where successfull!! (Exiting)")

            self.log.dieOnError("Jobs FJR check:  All retrieved jobs were unsuccessfull!")


        #self.nJobsFailedFJR = nFailedJobs

        self.nJobsSucceededFJR = nGoodJobs

        return total
    
    def getOutputLocation(self):

        if not self.doPublish:

            return self.outputlocation

        else:

            # parse publishname to get pnfs stageout dir
            split = self.publishName.split("/")

            #print split

            if len(split) > 0 and not self.publishName.rfind("/") == -1:

                part1 = '/pnfs/iihe/cms/store/user/'+self.getUserName()+'/'
                
                part2 = split[1]
            
                part3split = (split[2].split(self.getUserName()+"-"))#[1])#.split("-")

                #print part3split

                lastDir = part3split[len(part3split)-1].split("-")

                lastDir = lastDir[len(lastDir)-1]

                #print lastDir

                #if len(part3split) > 0:
                #    part3 = "/"+part3split[0]

                #    for i in range(1,len(part3split)-1):
                #        part3 += "-"+part3split[i]

                #    part3 += "/"+part3split[len(part3split)-1]

                if len(part3split) > 2:
                    part3 = "/"+part3split[1]+self.getUserName()+"-"+part3split[2].split("-"+lastDir)[0]+"/"+lastDir

                elif len(part3split) > 1:
                    part3 = "/"+part3split[1].split("-"+lastDir)[0]+"/"+lastDir
                    
                #print part1
                #print part2
                #print part3

                return part1+part2+part3

            return ""

    def getJobsDone(self):

        return self.nJobsDone

    def getJobsAborted(self):

        return self.nJobsAborted

    def getPublishedName(self):

        return self.publishName

    def getnEventsDBS(self):

        return self.nEventsDBS

    def getJobEff(self):

        nSubm = int(self.nJobsCreated)
        
        nSucc = int(self.nJobsSucceededFJR)
        
        jobEff = float(nSucc)/float(nSubm)

        return round(jobEff*100,2)

from logHandler import logHandler


#crab = CRABHandler("","",logHandler(""))

#crab.createMyProxyCredentials()

#print crab.getCrabJSON()

#crab.checkFJR()

#crab.nJobsCreated=5
#crab.nJobsFailedToSubmit=2
#crab.nJobsSucceededFJR=2

#print crab.getJobEff()
#crab.doPublish = bool(True)
#crab.publishName = "/TESTRUN_SCRIPT_18102011_153903/mmaes-RECO_TESTRUN_SCRIPT_18102011_153903_mmaes-TESTRUN_SCRIPT_18102011_153903-348ae4446003a8ef5cda190f78cdd378_20102011_102155-3cf4a0b0289a85abe00b4cd62dab7058/USER"
#print crab.getOutputLocation()
#crab.publishName = "/TESTRUN_SCRIPT_Summer11_20102011_113828/mmaes-TESTRUN_SCRIPT_Summer11_20102011_113828-348ae4446003a8ef5cda190f78cdd378/USER"
#print crab.getOutputLocation()
