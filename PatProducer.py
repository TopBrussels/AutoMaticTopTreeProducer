 # Class to handle PAT things

# interacting with the os
from subprocess import Popen, PIPE, STDOUT

from datetime import datetime

import sys

import os, os.path

class PatProducer:

    def __init__ (self,time,dir,logHandler):

        self.log = logHandler

        self.configFileName = ""
        self.outputFileName = ""

        self.timeStamp = time

        self.workingDir = dir

        self.initEnv = 'cd '+self.workingDir+'; eval `scramv1 runtime -sh`;'

        self.outputFileName = self.timeStamp+"_PAT.root"

    def output(self,string):

        #print "\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+string
        self.log.output(string)

    def createPatConfig (self,dataSet,globalTag,type,doGenEvent,cmssw_ver,cmssw_ver_sample,flavourFilterPath):

        cmsswver = int(cmssw_ver.split("_")[1])*100+int(cmssw_ver.split("_")[2])*10+int(cmssw_ver.split("_")[3])

        if (int(cmssw_ver.split("_")[2]) > 10):
            cmsswver = int(cmssw_ver.split("_")[1])*1000+int(cmssw_ver.split("_")[2])*10+int(cmssw_ver.split("_")[3])

        cmsswver_sample = int((cmssw_ver_sample.split("_")[1]).split("X")[0])

        #cmsswver = 220

        #print cmsswver
        #print cmsswver_sample

        self.configFileName =  (dataSet.split("/"))[1]+"-"+ (dataSet.split("/"))[2]+"_"+(globalTag.split("::"))[0]+"_"+self.timeStamp+"_PAT_cfg.py"

        if doGenEvent:
            type = type+"GenEvent"
            
        if len(cmssw_ver.split("--")) > 1:
            type = type+"_"+cmssw_ver.split("--")[1].strip("/")

        #if not doGenEvent:
        templateName = "ConfigTemplates/PatTemplate_CMSSW_"+str(cmsswver)+"_SampleVer_"+str(cmsswver_sample)+"X_SampleType_"+type+"_cfg.py"
        #else:
        #templateName = "ConfigTemplates/PatTemplate_CMSSW_"+str(cmsswver)+"_SampleVer_"+str(cmsswver_sample)+"X_SampleType_"+type+"GenEvent_cfg.py"

        self.output("--> Generating PAT configuration for "+dataSet+" using template "+templateName)

        if not os.path.exists(templateName):
            self.output(" ---> ERROR: template "+templateName+" does not exist, please check the templates in ConfigTemplates/")
            sys.exit(2)

        #process.GlobalTag.globaltag = cms.string('START311_V2::All')

        # bools to make shure we changed the appropriate things
        changedGlobalTag=bool(False)
        changedOutputFile=bool(False)
        
        template = open(templateName,"r") # open template
        patFile = open(self.workingDir+"/"+self.configFileName,'w') # open destination pat config

        nLine = int(0)
        inSideProcessBlock = bool(False)
        
        for line in template:

            nLine+=1
            
            # now we just write the line to the patcfg or alter it if needed

            # altering is done for: globaltag
            if line.rfind("process.GlobalTag.globaltag") == 0:

                patFile.write("process.GlobalTag.globaltag = cms.string(\'"+globalTag+"\')\n")

                changedGlobalTag = bool(True)
                
            # altering is done for: globaltag
            elif line.rfind("process.out.fileName") == 0:
                
                patFile.write('process.out.fileName = \"'+self.outputFileName+'\"\n')

                changedOutputFile = bool(True)
                
            # if not, just write the line to the patcfg
            
            else:

                if not flavourFilterPath == -1 and nLine == 3: # make shure the import of pat process skeleton was done and only do it once

                    self.output(" ---> Running Flavour History Tool Filter Path: "+str(flavourFilterPath))

                    patFile.write("\n# flavour history tool configuration \n")
                    patFile.write("process.load(\"PhysicsTools.HepMCCandAlgos.flavorHistoryPaths_cfi\")\n")
                    patFile.write("process.flavorHistoryFilter.pathToSelect = cms.int32("+str(flavourFilterPath)+")\n")

                # in the case of flhistorytool we need to adapt the process.p with the fltool sequence

                if not flavourFilterPath == -1 and not line.rfind("cms.Path(") == -1:

                    inSideProcessBlock = bool(True)

                if inSideProcessBlock and not line.rfind(")") == -1:

                    inSideProcessBlock=bool(False)

                    patFile.write("* process.flavorHistorySeq\n")
                
                patFile.write(line)

        # check if all is changed

        if not changedGlobalTag:
            patFile.write("process.GlobalTag.globaltag = cms.string(\'"+globalTag+"\')\n")

        if not changedOutputFile:
            patFile.write('process.out.fileName = \"'+self.outputFileName+'\"\n')

        template.close()
        patFile.close()
        
    def getConfigFileName (self):

        return self.configFileName

    def getOutputFileName (self):

        return self.outputFileName

    def dumpEventContent (self,dir):

        testFileName = str(os.listdir(dir)[0])

        cmd = self.initEnv+" edmDumpEventContent dcap://maite.iihe.ac.be"+dir+"/"+testFileName

        #print cmd

        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()

        #print out

        return out

#from logHandler import logHandler

#pat = PatProducer("123","CMSSW_3_11_2/src/test",logHandler(""))

#pat.createPatConfig("/test/test/AOD","BLA_V1::All","MC",0,"CMSSW_3_11_2","CMSSW_311X",-1)

#pat.dumpEventContent("/pnfs/iihe/cms/store/user/dhondt/InclusiveMu15/PAT_InclusiveMu15_Summer09-MC_31X_V3_7TeV_SD_Mu9-v1_16042010_005246/64c9fb455db43b65d5a7bd303ec52ca5/")
