# Class to handle TOPTREE things

# interacting with the os
from subprocess import Popen, PIPE, STDOUT

from datetime import datetime

import sys

import os, os.path

import math

class TopTreeProducer:

    def __init__ (self,time,dir,logHandler):

        self.log = logHandler

        self.configFileName = ""
        self.outputFileName = ""

        self.timeStamp = time

        self.workingDir = dir


	self.initEnv = 'cd '+self.workingDir+'; eval `scramv1 runtime -sh`;'

        self.nFilesInBlock=int(2)
    
    def output(self,string):

        #print "\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+string
        self.log.output(string)

    def createTopTreeConfig (self,dataSet,type,doGenEvent,globalTag,cmssw_ver,cmssw_ver_sample):

        cmsswver = int(cmssw_ver.split("_")[1])*100+int(cmssw_ver.split("_")[2])*10+int(cmssw_ver.split("_")[3])

        if (int(cmssw_ver.split("_")[2]) > 10):
            cmsswver = int(cmssw_ver.split("_")[1])*1000+int(cmssw_ver.split("_")[2])*10+int(cmssw_ver.split("_")[3])

        cmsswver_sample = int((cmssw_ver_sample.split("_")[1]).split("X")[0])

        #print cmsswver_sample

        #print cmsswver
        #cmsswver = 220

        #self.configFileName =  (dataSet.split("/"))[1]+"-"+ (dataSet.split("/"))[2]+"_"+self.timeStamp+"_TOPTREE_cfg.py"
        self.configFileName =  "TOPTREE_cfg.py"

        self.outputFileName = self.timeStamp+"_TOPTREE.root"

        if doGenEvent:
            type = type+"GenEvent"
            
        if len(cmssw_ver.split("--")) > 1:
            type = type+"_"+cmssw_ver.split("--")[1].strip("/")
        toptreerelease = cmssw_ver.split("--")
        productionrelease = "/home/dhondt/ProductionReleases/"+toptreerelease[1]+"/"+toptreerelease[0]
        
        templateName = productionrelease+"/src/TopBrussels/TopTreeProducer/prod/TOPTREE_cfg.py"
   
        #if not doGenEvent:
        #templateName = "ConfigTemplates/TopTreeProducerTemplate_CMSSW_"+str(cmsswver)+"_SampleVer_"+str(cmsswver_sample)+"X_SampleType_"+type+"_cfg.py"
        #else:
        #templateName = "ConfigTemplates/TopTreeProducerTemplate_CMSSW_"+str(cmsswver)+"_SampleVer_"+str(cmsswver_sample)+"X_SampleType_"+type+"GenEvent_cfg.py"
            
        self.output("--> Generating TopTreeProducer configuration for "+dataSet+" using template "+templateName)
    
        if not os.path.exists(templateName):
            self.output(" ---> ERROR: template "+templateName+" does not exist, please check the templates in ConfigTemplates/")
            sys.exit(2)
            
        #process.GlobalTag.globaltag = cms.string('START311_V2::All')

        # bools to make shure we changed the appropriate things
        changedGlobalTag=bool(False)
        changedOutputFile=bool(False)
        changedPoolSource=bool(False)
        
        template = open(templateName,"r") # open template
        TTFile = open(self.workingDir+"/"+self.configFileName,'w')# open destination toptree config

        inPoolSource = bool(False)
        
        for line in template:
            # now we just write the line to the toptreecfg or alter it if needed

            # altering is done for: globaltag
            if line.rfind("process.GlobalTag.globaltag") == 0:

                if not changedGlobalTag:
                    TTFile.write("process.GlobalTag.globaltag = cms.string(\'"+globalTag+"\')\n")

                changedGlobalTag = bool(True)
                
            # altering is done for: globaltag
            elif not line.rfind("RootFileName = cms.untracked.string") == -1: # now not == 0 because there are whitespaces in front

                if not changedOutputFile:
                    TTFile.write('\t\tRootFileName = cms.untracked.string(\"'+self.outputFileName+'\"),\n')

                changedOutputFile = bool(True)

            # change the poolsource -> useful for testrunning locally

            elif not line.rfind("process.source = cms.Source"):
                inPoolSource=bool(True)

                if not line.rfind("))") == -1: # meaning that the poolsource is one line

                    TTFile.write("process.source = cms.Source(\"PoolSource\",fileNames = cms.untracked.vstring(\'file:"+self.timeStamp+"_PAT.root\'))\n")
                    inPoolSource=bool(False)

                    changedPoolSource = bool(True)

            elif not line.rfind("fileNames = cms.untracked.vstring") == -1:

                if not changedPoolSource:

                    changedPoolSource = bool(True)
                
                    TTFile.write("process.source = cms.Source(\"PoolSource\",fileNames = cms.untracked.vstring(\'file:"+self.timeStamp+"_PAT.root\'))\n")


            elif inPoolSource and not line.rfind(")") == -1 and line.rfind("(") == -1 and line.rfind("fileNames") == -1:
                inPoolSource=bool(False)
                    
            # if not, just write the line to the patcfg, not if we are still in the poolsource

            elif not inPoolSource:

                TTFile.write(line)

        # check if all is changed

        if not changedGlobalTag:
            TTFile.write("process.GlobalTag.globaltag = cms.string(\'"+globalTag+"\')\n")

        if not changedOutputFile:
            TTFile.write('process.analysis.RootFileName = cms.untracked.string(\"'+self.outputFileName+'\")\n')
            
        template.close()
        TTFile.close()


    def getConfigFileName (self):

        return self.configFileName

    def getOutputFileName (self):

        return self.outputFileName


    def dumpEventContent (self,dir):

        self.output("--> Making a dump of the TopTree Branches")

        dcap = "dcap://maite.iihe.ac.be"

        compileDumper = ";export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.; cp ../src/libToto.so .; g++ `root-config --ldflags`  -L `pwd` -l Toto -I `root-config --incdir` `root-config --libs` TopTreeContentDump.C -o TopTreeContentDump; export DCACHE_RAHEAD=\"true\"; export DCACHE_RA_BUFFER=\"2500000\""
        
        testFile = ""
        
        for file in os.listdir(dir):
            
            if not file.rfind(".root") == -1:
                
                testFile = file
                
                break

        runDumper = "; srmcp srm://maite.iihe.ac.be:8443"+dir+"/"+testFile+" file:////$(pwd)/"+testFile+"; ./TopTreeContentDump --inputfiles "+testFile+"; rm "+testFile
        #runDumper = "; ./TopTreeContentDump --inputfiles "+dcap+dir+"/"+testFile

        cmd = ""

        # temp fix
        
        #if not self.workingDir.rfind("3_6_2") == -1:

        #cmd = "cd CMSSW_3_6_2; eval `scramv1 runtime -sh`; cd ../; cd "+self.workingDir+"/../../../../TopBrussels/TopTreeProducer/tools; ls; export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:."+compileDumper+runDumper
            
        #else:

	if not self.workingDir.rfind("CMSSW_5_") == -1:
            self.log.output("TopTreeProducer::CMSSW_5_X_Y release detected, setting scram arch to slc5_amd64_gcc462")
            self.initEnv = "export SCRAM_ARCH=\"slc5_amd64_gcc462\";"+self.initEnv        
    
        cmd = self.initEnv+" ls ; cd ../../../../TopBrussels/TopTreeProducer/src; make; cd ../tools; export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:."+compileDumper+runDumper

        #print cmd

        #cmd = ""
        
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()

        #print out
        
        begin = out.find("- TopTree")

        return out[begin:-1]

#from logHandler import logHandler

#top = TopTreeProducer("123","CMSSW_5_2_4_patch1_TopTreeProd_52X_v1/src/ConfigurationFiles/TTJets_TuneZ2star_8TeV-madgraph-tauola/Summer12-PU_S7_START52_V5-v1/02052012_153657/",logHandler(""))

#print top.dumpEventContent("/pnfs/iihe/cms/store/user/mmaes/TTJets_TuneZ2star_8TeV-madgraph-tauola/Summer12-PU_S7_START50_V15-v1/02052012_134053/TOPTREE/")

#print top.dumpEventContent("/pnfs/iihe/cms/store/user/dhondt/TTJets_TuneZ2star_8TeV-madgraph-tauola/Summer12-PU_S7_START52_V5-v1/03052012_103745/TOPTREE/")
