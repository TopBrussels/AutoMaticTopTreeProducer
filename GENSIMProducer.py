# Class to handle GENSIM things

# interacting with the os
from subprocess import Popen, PIPE, STDOUT

from datetime import datetime

import sys

import os, os.path

import math

class GENSIMProducer:

    def __init__ (self,time,dir,logHandler):

        self.log = logHandler

        self.configFileName = ""
        self.outputFileName = ""

        self.nLHEevents = int(0)
        self.nLHEeventsPerFile = int(0)

        self.LHEFiles = []

        self.LHEList = ""

        self.timeStamp = time

        self.workingDir = dir

	self.initEnv = 'cd '+self.workingDir+'; eval `scramv1 runtime -sh`;'
    
    def output(self,string):

        #print "\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+string
        self.log.output(string)

    def createConfig (self,publish,template,GlobalTag,LHEDir,nEvents):

        self.log.output("--> Generating GEN-SIM config with cmsDriver, template: "+template)

        cmd="cmsDriver.py Configuration/GenProduction/python/"+template+"  -s GEN,SIM --conditions "+GlobalTag+" --beamspot Realistic7TeV2011Collision --datatier GEN-SIM --eventcontent RAWSIM --no_exec --filein file:template.lhe"
        
        #print cmd
        
        pExe = Popen(self.initEnv+cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

        out = pExe.stdout.read()

        # replace LHE files in template, only taking 6 now...

        for file in os.listdir(LHEDir):

            if not file.rfind(".lhe") == -1:

                if len(self.LHEFiles) < 7:
                    self.LHEFiles.append(file.strip())

        #print LHEFiles

        firstFile = bool(True)
        
        for lhe in self.LHEFiles:

            for line in open(LHEDir+"/"+lhe):

                if not line.rfind("<event>") == -1:
 
                    self.nLHEevents = self.nLHEevents+1

                    if firstFile:
                        self.nLHEeventsPerFile = self.nLHEeventsPerFile+1

            firstFile = bool(False)
            
        self.configFileName = template.split(".py")[0]+"_py_GEN_SIM.py"
	self.outputFileName = template.split(".py")[0]+"_py_GEN_SIM.root"

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
                        self.LHEList = self.LHEList+LHEDir+"/"+self.LHEFiles[i]+","
                    else:
                        files = files+"\t\t'file:"+self.LHEFiles[i]+"'\n"
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

	
