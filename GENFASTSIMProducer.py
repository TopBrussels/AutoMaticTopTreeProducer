# Class to handle GEN-FASTSIM things

# interacting with the os
from subprocess import Popen, PIPE, STDOUT

from datetime import datetime

import sys

import os, os.path

import math

class GENFASTSIMProducer:

    def __init__ (self,time,dir,logHandler,setarchitecture):

        self.log = logHandler

        self.configFileName = ""
        self.outputFileName = ""

        self.nLHEevents = int(0)
        self.nLHEeventsPerFile = int(0)

        self.LHEFiles = []

        self.LHEList = ""

        self.timeStamp = time

        self.workingDir = dir
				
        self.setarchitecture = setarchitecture

	self.initEnv = 'cd '+self.workingDir+'; eval `scramv1 runtime -sh`;'
    
    def output(self,string):

        #print "\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+string
        self.log.output(string)

    def createConfig (self,publish,template,GlobalTag,LHEDir,nEvents,campaign):

        self.log.output("--> Generating GEN-FASTSIM-HLT config with cmsDriver, template: "+template)

        if campaign == "Summer12":
				   cmd="cmsDriver.py Configuration/GenProduction/python/EightTeV/"+template+"  -s GEN,FASTSIM,HLT:7E33v2 --conditions "+GlobalTag+" --beamspot Realistic8TeVCollision --pileup 2012_Startup_inTimeOnly --datamix NODATAMIXER --datatier AODSIM --eventcontent AODSIM --no_exec --filein file:template.lhe"
        else:
				   self.log.output(" ---> ERROR: campaign "+campaign+" not supported. Supported campaigns: Summer12")
				
        #print cmd
        
        pExe = Popen(self.setarchitecture+self.initEnv+cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

        out = pExe.stdout.read()

        gzipdetected = bool(False)
				# replace LHE files in template, only taking 6 now... -> updated: only 10 (the lhe files are only 50k, in the past 100k, maybe this will work)
        for file in os.listdir(LHEDir):

            if not file.rfind(".lhe") == -1:

                if len(self.LHEFiles) < 12:
                    if not file.rfind(".lhe.gz") == -1:
                        self.log.output(" ---> WARNING: gzipped LHE file detected, copying and unzipping in local directory for crab")
                        Popen("cp "+LHEDir+"/"+file+" "+self.workingDir, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
                        Popen("gunzip "+self.workingDir+"/"+file, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
                        filename = (file.split(".gz"))[0].strip()
                        gzipdetected = True
			
                        #do a fix when seed number was not 0: stripping a certain line from the runcard (seed number), in principle also to be done when not using gzipped lhe files for safety; not supported right now...
                        self.log.output("   -----> Removing random seed line in LHE file...")
                        origf = open(self.workingDir+"/"+filename,"r")
                        origlines = origf.readlines()
                        origf.close()
                        workingf = open(self.workingDir+"/"+filename,"w")
                        for line in origlines:
                           if line.rfind("rnd seed (0=assigned automatically=default)") == -1:
                               workingf.write(line)
                    else:
                        filename = file.strip()
										
                    #self.LHEFiles.append(file.strip())
                    self.LHEFiles.append(filename)

        #print self.LHEFiles
				
        if gzipdetected:
            LHEDir = self.workingDir				

        firstFile = bool(True)
        
        for lhe in self.LHEFiles:

            for line in open(LHEDir+"/"+lhe):

                if not line.rfind("<event>") == -1:
 
                    self.nLHEevents = self.nLHEevents+1

                    if firstFile:
                        self.nLHEeventsPerFile = self.nLHEeventsPerFile+1

            firstFile = bool(False)
            
        self.configFileName = template.split(".py")[0]+"_py_GEN_FASTSIM_HLT_PU.py"
	self.outputFileName = template.split(".py")[0]+"_py_GEN_FASTSIM_HLT_PU.root"

        file = "./"+self.workingDir+"/"+self.configFileName

        
        Popen("cd "+self.workingDir+"; mv -v "+self.configFileName+"* TMP", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

        #print self.configFileName

        out = open(self.workingDir+"/"+self.configFileName,"w")

        for line in open(self.workingDir+"/TMP"):

            if not line.rfind("LHESource") == -1:

                out.write("process.source = cms.Source(\"LHESource\",\n\tskipEvents = cms.untracked.uint32(0),\n")

            elif not line.rfind("template.lhe") == -1 and not line.rfind("vstring") == -1:

                #print line
                
                files = "\tfileNames = cms.untracked.vstring(\n"

                for i in xrange(len(self.LHEFiles)):

                    if not i == len(self.LHEFiles)-1:
                        files = files+"\t\t'file:"+self.LHEFiles[i]+"',\n"
                        if gzipdetected:
                           self.LHEList = self.LHEList+self.LHEFiles[i]+","
                        else:
                           self.LHEList = self.LHEList+LHEDir+"/"+self.LHEFiles[i]+","
                    else:
                        files = files+"\t\t'file:"+self.LHEFiles[i]+"'\n"
                        if gzipdetected:
                           self.LHEList = self.LHEList+self.LHEFiles[i]
                        else:
                           self.LHEList = self.LHEList+LHEDir+"/"+self.LHEFiles[i]

                files = files+"\t)\n"

                #print self.LHEList

                out.write(files)

            else:

                out.write(line)

        os.remove(self.workingDir+"/TMP")
        
        out.close()
        
    def getConfigFileName (self):

        return self.configFileName

    def getOutputFileName (self):

        return self.outputFileName

    def getNLHEevents (self):

        return self.nLHEevents

    def getNLHEeventsPerFile (self):

        return self.nLHEeventsPerFile

    def getlhefiles (self):

        return self.LHEList
	
