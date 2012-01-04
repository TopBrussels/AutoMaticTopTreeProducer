# Class to handle GENSIM things

# interacting with the os
from subprocess import Popen, PIPE, STDOUT

from datetime import datetime

import sys

import os, os.path

import math

class RECOProducer:

    def __init__ (self,time,dir,logHandler):

        self.log = logHandler

        self.configFileName = ""
        self.outputFileName = ""

        self.timeStamp = time

        self.workingDir = dir

	self.initEnv = 'cd '+self.workingDir+'; eval `scramv1 runtime -sh`;'
    
    def output(self,string):

        #print "\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+string
        self.log.output(string)

    def createConfig (self,campaign,GlobalTag):

        template="./ConfigTemplates/RECO/"+campaign+".txt"

        if not os.path.exists(template):
            self.log.output("RECOProducer: ERROR -- No template for "+campaign)
            sys.exit(2)

        self.log.output("--> Generating RECO config from template: "+template)

        self.configFileName = "RECO_config_"+campaign+"_"+self.timeStamp+"_cff.py"

        out = open(self.workingDir+"/"+self.configFileName,"w")

        inBlock = bool(False)
        for line in open(template):

            if not line.rfind("process.RECOSIMoutput") == -1:
                inBlock=bool(True)

            if inBlock and not line.rfind("fileName") == -1:

                self.outputFileName = line.split("'")[1]

                inBlock=bool(False)

            if not line.rfind("process.GlobalTag") == -1:
                out.write("process.GlobalTag.globaltag = '"+GlobalTag+"'\n")
            else:
                out.write(line)
            
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

	
