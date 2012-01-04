# python script to remove obsolete productions

# will only work from the central account ;-)

# for command line options
from optparse import OptionParser

# regular expressions
import re

# interacting with the os
from subprocess import Popen, PIPE, STDOUT
import sys
import os, os.path

# time
import time, datetime

# import crabhandler for proxy stuff

from CrabHandler import CRABHandler
from logHandler import logHandler

log = logHandler("")

baseDir = "../CMSSW_3_6_0/src/TopBrussels/TopTreeProducer/"

baseDir = sys.argv[1]

#initEnv = 'cd '+baseDir+'; eval `scramv1 runtime -sh`;'
initEnv = 'cd '+baseDir+'/../../../../CMSSW_3_6_2; eval `scramv1 runtime -sh`; cd ../tools; cd '+baseDir+';'


if not os.path.exists(baseDir+"/tools/TopTreeContentDump.C"):

    log.output("Please use a TopTreeProducer version >= CMSSW_36X_v0 to have the TopTreeContentDump tool!")

else:

    dir = "/pnfs/iihe/cms/store/user/dhondt/WJets-madgraph/dhondt-PAT_WJets-madgraph_Summer09-MC_31X_V3_7TeV-v3_14042010_113732-64c9fb455db43b65d5a7bd303ec52ca5/28042010_183656/TOPTREE/"

    #dir = "/pnfs/iihe/cms/store/user/dhondt/WJets-madgraph/dhondt-PAT_WJets-madgraph_Summer09-MC_31X_V3_7TeV-v3_14042010_113732-64c9fb455db43b65d5a7bd303ec52ca5/15042010_164539/TOPTREE/"

    #dir = "/pnfs/iihe/cms/store/user/dhondt/TTbarJets-madgraph/dhondt-PAT_TTbarJets-madgraph_Summer09-MC_31X_V3_7TeV-v5_09042010_205141-f7b65dd65b478b6eda778f65a63587d3/27042010_215421/TOPTREE"

    dir = sys.argv[2]

    toRM = ""

    log.output("-> Looking for duplicated files in Directory: "+dir)

    for i in os.listdir(dir):

        if i.rfind(".root") == -1:
            continue

        ## LOOKING FOR DUPLICATE FILES
            
        splitName = i.split("_")[3]

        #print i.split("_")

        cmd = "ls -tr "+dir+" | grep root | grep TOPTREE_"+splitName+"_"

        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()

        fileList = out.split("\n")

        #print fileList
        
        if not len(fileList)-1 == 1:

            log.output("  ---> File "+i+" might be duplicated")

            ## CHECK WHICH IS THE LATEST RESUBMIT
            
            highest = int(0);

            for duplicate in fileList:

                nSubmit = ""

                if not duplicate == "":

                    if  not len(duplicate.split("_")[4].split(".root")) == 1:
                        
                        nSubmit = duplicate.split("_")[4].split(".root")[0]

                    else:

                        nSubmit = duplicate.split("_")[4]

                    #print nSubmit
                    
                    if int(nSubmit) > highest:

                        highest = int(nSubmit)

            #print highest

            # remove all submissions below nSubmit

            for duplicate in fileList:

                if not duplicate == "":

                    nSubmit = ""

                    if  not len(duplicate.split("_")[4].split(".root")) == 1:
                        
                        nSubmit = duplicate.split("_")[4].split(".root")[0]

                    else:

                        nSubmit = duplicate.split("_")[4]

                    if int(nSubmit) < highest:

                        if toRM.rfind(duplicate) == -1:
                        
                            toRM += duplicate+";"

                            log.output("   ----> Adding file "+duplicate+" to the list of files to be removed")

                    elif int(nSubmit) == highest and duplicate != fileList[len(fileList)-2]:

                        if toRM.rfind(duplicate) == -1:
                        
                            toRM += duplicate+";"
                            
                            log.output("   ----> Adding file "+duplicate+" to the list of files to be removed")


                    #print fileList
                    #print "a "+fileList[len(fileList)-2]
                    #print "b "+duplicate


    #print toRM
    
    BadFileList = toRM.split(";")

    srm = "srm://maite.iihe.ac.be:8443"

    if len(BadFileList)-1 > 0:
        log.output("-> Let's kill some duplicated files!!!")

    for i in xrange ( len(BadFileList)-1 ):

        badFile = BadFileList[i]

        newFileName = badFile.split(".root")[0]+".BADFILE"

        log.output(" --> ByeBye "+badFile)

        cmd = "srmmv "+srm+dir+"/"+badFile+" "+srm+dir+"/"+newFileName

        #print cmd

        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()

        log.output(out)


    log.output("-> Looking for corrupted files in Directory: "+dir)

    toRM = ""
    
    nGoodFiles = int(0)

    nEventsTotal = int(0)

    cmd = "cp dumpEvents.C "+baseDir+"/tools ;"+initEnv+' export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.; cd tools/; cp ../src/libToto.so .; g++  -L `pwd` -l Toto -I `root-config --incdir` `root-config --libs` dumpEvents.C -o dumpEvents'
        
    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    out = pExe.stdout.read()

    cmd = "ls "+dir+"/*.root | wc -l"

    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    out = pExe.stdout.read()

    nFiles = int(out)

    nCurrentFile = int(0)

    for i in os.listdir(dir):

        if i.rfind(".root") == -1:
            continue
        
        ## LOOKING FOR CORRUPTED FILES

        nCurrentFile += 1

        log.output("    ----> Checking file "+str(nCurrentFile)+"/"+str(nFiles)+" (Accumulated #events: "+str(nEventsTotal)+")")
        
        cmd = initEnv+'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.; cd tools/; ./dumpEvents --inputfiles dcap://maite.iihe.ac.be'+dir+i
        
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()
        
        #print cmd
        #print out

        output = out.split('\n')
        
        if not int(pExe.poll()) == 0:
        
            log.output("  ---> File "+i+" seems to corrupt, removing it at the end!")
            log.output(cmd)
      	    log.output(out)

            if toRM.rfind(i) == -1:
        
                toRM += i+";"

        else:

            tmpName = output[len(output)-2].split(' ')[0].split("/")

            fileName = tmpName[len(tmpName)-1]

            nEvents = output[len(output)-2].split(' ')[1]

            #log.output("  ---> File "+fileName+" contains "+nEvents+" events.")

            nGoodFiles += 1

            nEventsTotal += int(nEvents)


    log.output(" --> The script found "+str(nGoodFiles)+" good files containing in total "+str(nEventsTotal)+" events.")

    BadFileList = toRM.split(";")

    srm = "srm://maite.iihe.ac.be:8443"

    if len(BadFileList)-1 > 0:
        log.output("-> Let's kill some duplicated files!!!")

    for i in xrange ( len(BadFileList)-1 ):

        badFile = BadFileList[i]

        newFileName = badFile.split(".root")[0]+".BADFILE"

        log.output(" --> ByeBye "+badFile)

        cmd = "srmmv "+srm+dir+"/"+badFile+" "+srm+dir+"/"+newFileName

        #print cmd

        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()

        log.output(out)
