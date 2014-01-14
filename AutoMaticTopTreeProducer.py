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

# import DNS parse
from DBSHandler import DBSHandler

# import CRAB handler
from CrabHandler import CRABHandler

# import PAT class
from PatProducer import PatProducer

# import TopTree class
from TopTreeProducer import TopTreeProducer

# import logHandler
from logHandler import logHandler

# import mailHandler
from MailHandler import MailHandler

# import interface to topDB
from sqlHandler import topDBInterface

################################
## PLACE TO PUT THE FUNCTIONS ##
################################

#############
## METHODS ##
#############

def setupDirs(baseDir):

    global workingDir

    dir = []

    dir.append(baseDir+"/ConfigurationFiles")

    dir.append(dir[len(dir)-1]+"/"+(options.dataset).split("/")[1])

    dir.append(dir[len(dir)-1]+"/"+(options.dataset).split("/")[2])

    dir.append(dir[len(dir)-1]+"/"+timestamp)
    
    for i in range(0,len(dir)):

        if not os.path.exists(dir[i]):

            log.output(" --> Creating directory: ./"+dir[i])

            os.makedirs(dir[i])

    workingDir = dir[len(dir)-1]

def checkCommandLineOptions(options):

    global dataType
    global doDry

    log.output("********** Settings **********")
    
    log.output("--> CMSSW Version: "+options.cmssw_ver)
    
    log.output("--> DataSet Name: "+options.dataset)

    dataTier = ((options.dataset).split("/"))[3]

    isReco = False

    isGen = False

    isPAT = False

    isAOD = False

    for tier in dataTier.split("-"):

        if tier == "RECO":

            isReco = True

        elif tier == "GEN":

            isGen = True

    if dataTier == "USER":
        if doStartFromPAT:
            isPAT = True
            
        if not doStartFromPAT and options.DataTier == "NOTFILLED":
            log.output("-> ERROR: Please provide a DataTier with -t <DataTier> when providing a USER dataset")
            sys.exit(1)

        else:
            
            if not options.DataTier.rfind("PAT") == -1:
                isPAT = True

            if not options.DataTier.rfind("RECO") == -1:
                isReco = True

            if not options.DataTier.rfind("GEN") == -1:
                isGen = True

            if not options.DataTier.rfind("AOD") == -1:
                isAOD = True
                isReco = True

            if not options.DataTier.rfind("AODSIM") == -1:
                isAOD = True
                isGen = True

    if dataTier == "AOD":

        isAOD = True
        isReco = True

    elif dataTier == "AODSIM":
 
        isAOD = True
        isGen = True

    #if isAOD:
    #    dataType = "AOD"
        
    if not doStartFromPAT:

        if isGen is True:

            log.output(" ---> The script determined that it is an MC dataset.")

            dataType += "MC"

        elif isReco is True:

            log.output(" ---> The script determined that it is real data.")

            dataType += "data"

        elif isReco is False:
            log.output(" ---> ERROR: Please provide a dataset with a RECO dataTier.")

            dieOnError("Invalid input dataset: Please provide data with a RECO datatier.")

    else:

        if not isPAT:

            log.output(" ---> ERROR: When using --start-from-pat, use a pat sample with -d.")

            dieOnError("Invalid input dataset: Please provide a PAT dataset when using --start-from-pat")

        else:

            if options.startFromPatMC:
                dataType="MC"
                log.output(" ---> The script determined that it is a PAT-MC dataset.")

            else:

                log.output(" ---> The script determined that it is a PAT dataset.")

    if not doStartFromPAT:
        log.output("--> Global Tag: "+options.GlobalTag)

    if doDry:

        log.output("--> This is a DRY run, no crab jobs will be submitted!!")

def doStartupChecks(productionrelease):

    global doStartFromPAT

    log.output("********** Checking environment **********")

    log.output("--> Checking if you have a "+productionrelease+" release.")

    if (os.path.isdir(productionrelease)):
        log.output(" ---> Ok, the release is present!")
        cmd ='cd '+productionrelease+'/src; cmsenv'
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    else:
        log.output(" ---> ERROR: Please scram the proper release first! (Exiting)")
        dieOnError("Environment: resquested CMSSW version is not found in the working directory")

    log.output("--> Checking if "+productionrelease+"/src contains the TopTreeProducer package.")

    if (os.path.isdir(productionrelease+TopTreeProducerDir)):
        log.output(" ---> Ok, the "+TopTreeProducerDir+" directory exists!")
    else:
        log.output(" ---> ERROR: Please ensure that you have the TopTreeProducer package installed! (Exiting)")
        dieOnError("Environment: resquested CMSSW version does not contain the TopTreeProducer package")


    log.output("--> Checking if "+productionrelease+" contains the PatAlgos package.")

    if (os.path.isdir(productionrelease+PatDir)):
        log.output(" ---> Ok, the "+PatDir+" directory exists!")
    else:
        log.output(" ---> ERROR: Please ensure that you have the PatAlgos package installed! (Exiting)")
        dieOnError("Environment: resquested CMSSW version does not contain the PatAlgos package")


    log.output("--> Checking DBS to see wether the requested Dataset exists")

    if dbsInst == "":
        dbsMgr = DBSHandler("cms_dbs_prod_global");
    else:
        dbsMgr = DBSHandler(dbsInst);

    if doStartFromPAT:

        dbsMgr.setDBSInst("cms_dbs_ph_analysis_02")

    if not dbsMgr.datasetExists(options.dataset):
        log.output(" ---> ERROR: "+options.dataset+" was not found in DBS! (Exiting)")
        dieOnError("Dataset: DBS query for your dataset returned an empty set.")

    else:
        log.output(" ---> Ok, Dataset was found!")

    log.output("--> Checking status of CRABServer (not yet implemented)")

    crab = CRABHandler("","",log)

    crab.checkGridProxy(False)

    crab.checkCredentials(False)

def processPAT(isnew):

    global workingDir
    global dbsInst
    global dataType
    global doDry
    global patPublishName
    global nEventsPAT
    global nEventsDBS
    global patCffName
    global patLocation
    global patEventContent
    global jobEffPat
    global options
    global CrabJSON

    
    log.output("********** Preparing to produce the PAT-tuple **********")

    startTime = gmtime()

    pat = PatProducer(timestamp,workingDir,log);

    pat.createPatConfig(options.dataset,options.GlobalTag,dataType,options.doGenEvent,options.cmssw_ver,options.cmssw_ver_sample,options.flavourHistoryFilterPath,isnew)

    patCffName = pat.getConfigFileName()

    crab = CRABHandler(timestamp,workingDir,log);

    #print "**"+crab.baseDir
    if not dbsInst == "":

        crab.setDBSInst(dbsInst)

        log.output(" ---> CRAB will use DBS instance "+dbsInst+" to look for your data.")

    if not doDry:
        
        crab.scaleJobsSize(options.dataset,options.RunSelection,1) # if to much jobs (>2500) we create new cfg with 2500 jobs

    crab.AdditionalCrabInput=getAdditionalInputFiles(crab.AdditionalCrabInput)

    crab.createCRABcfg("crab_pat_"+timestamp+".cfg",
                   options.dataset,
                   pat.getConfigFileName(),
                   pat.getOutputFileName(),
                   "PAT",
                   bool(True),
                   options.CEBlacklist,
                   options.RunSelection,
                   options.forceStandAlone,
                   toptreeTag)

    if not doDry:
        
        crab.submitJobs()

        nEventsDBS = crab.getnEventsDBS()

        crab.checkJobs()

        time.sleep(60) # to be shure the jobs are in done status

        patPublishName = crab.publishDataSet()

        nEventsPAT = crab.checkFJR()

        patLocation = crab.getOutputLocation()

        patEventContent = pat.dumpEventContent(patLocation)

        jobEffPat = crab.getJobEff()

        log.output("--> Job Efficiency: "+str(crab.getJobEff()))

    endTime = gmtime()

    log.output("--> The PAT production took "+ str((time.mktime(endTime)-time.mktime(startTime))/3600.0)+" hours.")

    log.appendToMSG("\n* PAT production information: ")
    
    if not crab.getOutputLocation() == "":

        log.appendToMSG("\n\t-> Data location: "+patLocation+"\n")

    log.appendToMSG("\t-> DataSet was published in DBS as: "+patPublishName)
        
    log.appendToMSG("\t-> Number of events processed: "+str(nEventsPAT))
        
def processTOPTREE(isnew):

    log.output("********** Preparing to produce the TopTree **********")

    startTime = gmtime()

    global workingDir
    global dataType
    global doDry
    global nEventsDBS
    global nEventsTT
    global doPBS
    global topTreeLocation
    global topCffName
    global options
    global ttreeEventContent
    global jobEffTT
    global CrabJSON

    top = TopTreeProducer(timestamp,workingDir,log)
            
    top.createTopTreeConfig(options.dataset,dataType,options.doGenEvent,options.GlobalTag,options.cmssw_ver,options.cmssw_ver_sample,isnew)

    topCffName = top.getConfigFileName()

    crab = CRABHandler(timestamp,workingDir,log);
    
    useDataSet=""

    if doStartFromPAT:

        useDataSet=options.dataset

    else:

        useDataSet=patPublishName

    options.RunSelection = ""
        
    crab.setDBSInst("cms_dbs_ph_analysis_02")
        
    type = "TOPTREE"

    if not doDry:
            
        crab.scaleJobsSize(useDataSet,options.RunSelection,10) # if to much jobs (>2500) we create new cfg with 2500 jobs

    crab.AdditionalCrabInput=getAdditionalInputFiles(crab.AdditionalCrabInput)

    crab.createCRABcfg("crab_toptree_"+timestamp+".cfg",
                       useDataSet,
                       top.getConfigFileName(),
                       top.getOutputFileName(),
                       type,
                       bool(False),
                       options.CEBlacklist,
                       options.RunSelection,
                       options.forceStandAlone,
                       toptreeTag) # empty runselection for top

    topTreeLocation = crab.getOutputLocation().split("\n")[0]
        
    if not doDry:

        crab.submitJobs()

        crab.checkJobs()

        #time.sleep(60) # to be shure the jobs are in done status

        crab.publishDataSet()

        CrabJSON = crab.getCrabJSON()        

        nEventsTT = crab.checkFJR()

        if doStartFromPAT:
            nEventsDBS = crab.getnEventsDBS()

        ttreeEventContent = top.dumpEventContent(topTreeLocation)

        jobEffTT = crab.getJobEff()

        log.output("--> Job Efficiency: "+str(crab.getJobEff()))
        
    endTime = gmtime()

    log.output("--> The TopTree production took "+ str((time.mktime(endTime)-time.mktime(startTime))/3600.0)+" hours.")

    log.appendToMSG("\n* TopTree production information: \n")

    if not crab.getOutputLocation() == "":

        log.appendToMSG("\t-> Data location: "+topTreeLocation+"\n")

    log.appendToMSG("\t-> Number of events processed: "+str(nEventsTT))

def processPATandTOPTREE(isnew):

    global workingDir
    global dbsInst
    global dataType
    global doDry
    global nEventsDBS
    global workingDir
    global dataType
    global nEventsTT
    global nEventsDBS
    global topTreeLocation
    global topCffName
    global patCffName
    global ttreeEventContent
    global options
    global jobEffPat
    global jobEffTT
    global CrabJSON
    
    log.output("********** Preparing to produce the PAT-tuple and TopTree in one go **********")

    startTime = gmtime()

    # create pat cfg
    
    pat = PatProducer(timestamp,workingDir,log);

    pat.createPatConfig(options.dataset,options.GlobalTag,dataType,options.doGenEvent,options.cmssw_ver,options.cmssw_ver_sample,options.flavourHistoryFilterPath,isnew)

    patCffName = pat.getConfigFileName()

    # create toptree cfg

    top = TopTreeProducer(timestamp,workingDir,log)
            
    top.createTopTreeConfig(options.dataset,dataType,options.doGenEvent,options.GlobalTag,options.cmssw_ver,options.cmssw_ver_sample,isnew)

    topCffName = top.getConfigFileName()

    log.output(" ---> will expand the TopTree config before sending it with crab " )
    #cmd2 = 'cd '+options.cmssw_ver+'; eval `scramv1 runtime -sh`; cd -; python '+workingDir+'/'+top.getConfigFileName()+'; mv -v expanded.py '+workingDir+'/'
    cmd2 = 'cd '+productionrelease+"/src"+'; eval `scramv1 runtime -sh`; cd -; python '+workingDir+'/'+top.getConfigFileName()+'; mv -v expanded.py '+workingDir+'/'
    if not workingDir.rfind("CMSSW_5_") == -1:
        log.output("Expanding TopTree config:: CMSSW_5_X_Y release detected, setting scram arch to slc5_amd64_gcc462")
        cmd2 = "export SCRAM_ARCH=\"slc5_amd64_gcc462\";"+cmd2

    pExe = Popen(cmd2, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True) 
    log.output(pExe.stdout.read())
		
		# create crab cfg

    crab = CRABHandler(timestamp,workingDir,log);

    if not dbsInst == "":

        crab.setDBSInst(dbsInst)

        log.output(" ---> CRAB will use DBS instance "+dbsInst+" to look for your data.")

    #crab.nEventsPerJob = "20000"
    #crab.nEventsPerJob = "500"

    if not doDry:
        
        crab.scaleJobsSize(options.dataset,options.RunSelection,1) # if to much jobs (>2500) we create new cfg with 2500 jobs

    crab.runTwoConfigs(patCffName,topCffName)
    
    crab.AdditionalCrabInput=getAdditionalInputFiles(crab.AdditionalCrabInput)
                                
    crab.createCRABcfg("crab_"+timestamp+".cfg",
                       options.dataset,
                       pat.getConfigFileName(),
                       top.getOutputFileName(),
                       "TOPTREE",
                       bool(False),
                       options.CEBlacklist,
                       options.RunSelection,
                       options.forceStandAlone,
                       toptreeTag)

    
    topTreeLocation = crab.getOutputLocation().split("\n")[0]
        
    if not doDry:

        crab.submitJobs()

        crab.checkJobs()

        crab.publishDataSet()

        nEventsDBS = crab.getnEventsDBS()

        nEventsTT = crab.checkFJR()

        CrabJSON = crab.getCrabJSON()

        if doStartFromPAT:
            nEventsDBS = crab.getnEventsDBS()

        ttreeEventContent = top.dumpEventContent(topTreeLocation)

        jobEffPat = crab.getJobEff() # same job-eff for pat & TT in case of duo-jobs

        jobEffTT = crab.getJobEff()

        log.output("--> Job Efficiency: "+str(crab.getJobEff()))
        
    endTime = gmtime()

    log.output("--> The TopTree production took "+ str((time.mktime(endTime)-time.mktime(startTime))/3600.0)+" hours.")

    log.appendToMSG("\n* TopTree production information: \n")

    if not crab.getOutputLocation() == "":

        log.appendToMSG("\t-> Data location: "+topTreeLocation+"\n")

    log.appendToMSG("\t-> Number of events processed: "+str(nEventsTT))

    log.appendToMSG("\n Note: This TopTree was created from PAT inside one single job, the PATtuple was not stored")
   
def announceDataSet():

    log.output("********** Sending announcement for this production **********")

    global options
    global logFileName
    global patPublishName
    global nEventsPAT
    global nEventsTT
    global nEventsDBS
    global doStartFromPAT
    global timestamp

    mail = MailHandler()

    type = "announcement"

    subject = "New dataset announcement"

    msg = "Dear top quark group,\n"
    msg += "\n"
    msg += "This is an automatically generated e-mail to announce that a TopTree production is completed."
    msg += "\n\n* Input parameters:"

    msg += "\n\n\t-> Input dataset: "+options.dataset +" (#Events: "+str(nEventsDBS)+")"

    msg += "\n\n\t-> Global Tag: "+options.GlobalTag

    msg += "\n\n\t-> CMSSW Version: "+options.cmssw_ver

    msg += log.getAnnouncementMSG()

    if not options.flavourHistoryFilterPath == -1:

        msg += "\n\nNote: The Flavour History Tool was enabled within the production, filer path: "+str(options.flavourHistoryFilterPath)+" !!\n"

    msg += "\n\nMore information on this production can be found on https://mtop.iihe.ac.be/TopDB."

    msg += "\n\n\nCheers,\nThe TopTreeProduction team"
   
    mail.sendMail(type,subject,msg)

def updateTopDB(type): # type = pat or toptree

    log.output("********** Adding the information to TopDB **********")

    global options
    global logFileName
    global patPublishName
    global nEventsPAT
    global nEventsTT
    global nEventsDBS
    global doStartFromPAT
    global timestamp
    global workingDir
    global topTreeLocation
    global patLocation
    global ttreeEventContent
    global patEventContent
    global jobEffPat
    global jobEffTT
    
    db = topDBInterface()
        
    patTAG=""
    topTAG=""

    cmd ='cd '+workingDir+'; eval `scramv1 runtime -sh`; showtags >> tags'

    if not workingDir.rfind("CMSSW_5_") == -1:
        log.output("updateTopDB:: CMSSW_5_X_Y release detected, setting scram arch to slc5_amd64_gcc462")
        cmd = "export SCRAM_ARCH=\"slc5_amd64_gcc462\";"+cmd
    
    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    out = pExe.stdout.read()

    for line in open(workingDir+"/tags","r"):
        if not line.rfind("PatAlgos") == -1:
            patTAG=line
        if not line.rfind("TopTreeProducer") == -1:
            topTAG=line

    os.remove(workingDir+"/tags")

    # get current dir

    cmd ='pwd'
    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    dir = pExe.stdout.read()

    # insert dataset into topDB if not present (obsolete)

    #if skipPAT:
        
    #    db.insertDataSet("TopTree Producer",options.dataset,options.cmssw_ver,"Reco","Produced",0)

    #elif not doStartFromPAT:
    #    db.insertDataSet("TopTree Producer",options.dataset,options.cmssw_ver,"Reco","PATified",1)

    # insert patuple in topDB

    if type == "pat":

        if not doStartFromPAT:

            db.insertPatTuple("TopTree Producer",options.dataset,patPublishName,patTAG,options.cmssw_ver,patLocation,dir+'/'+workingDir+'/'+patCffName,nEventsDBS,nEventsPAT,jobEffPat,patEventContent,CrabJSON,options.RunSelection)
            
    # insert toptree in topdb

    comment = ""

    if not options.flavourHistoryFilterPath == -1:
        comment += "flavorHistoryPath:"+str(options.flavourHistoryFilterPath)+"\n"

    if type == "toptree":

        comment += ""
        
        if doStartFromPAT:
            db.insertTopTree("TopTree Producer",db.searchPATOrigin(options.dataset),options.dataset,options.cmssw_ver,topTAG,topTreeLocation,topTreeLocation,nEventsTT,jobEffTT,dir+'/'+workingDir+'/'+topCffName,comment,ttreeEventContent,CrabJSON,options.RunSelection)
        else:
            db.insertTopTree("TopTree Producer",options.dataset,patPublishName,options.cmssw_ver,topTAG,topTreeLocation,topTreeLocation,nEventsTT,jobEffTT,dir+'/'+workingDir+'/'+topCffName,comment,ttreeEventContent,CrabJSON,options.RunSelection)

    if type == "pat+toptree":

        #comment += "\nTopTree Created from PAT in one single run, PAT was not stored!!!!"

        db.insertPatTuple("TopTree Producer",options.dataset,"PaTuple "+timestamp+" Not Published in DBS",patTAG,options.cmssw_ver,"PaTuple not stored on storage",dir+'/'+workingDir+'/'+patCffName,nEventsDBS,nEventsTT,jobEffPat,"PaTuple not stored on storage",CrabJSON,options.RunSelection)
        
        db.insertTopTree("TopTree Producer",options.dataset,"PaTuple "+timestamp+" Not Published in DBS",options.cmssw_ver,topTAG,topTreeLocation,topTreeLocation,nEventsTT,jobEffTT,dir+'/'+workingDir+'/'+topCffName,comment,ttreeEventContent,CrabJSON,options.RunSelection)

def dieOnError(string):

    global doDry
    global log

    if doDry:

        log.dieOnError(string)

    else:

        log.dieOnError(string)

def getAdditionalInputFiles (AdditionalCrabInput):

    tmpl=str(os.path.realpath(__file__).split("AutoMaticTopTreeProducer.py")[0])+"ConfigTemplates"
    for file in os.listdir(tmpl):
        if not file.rfind(".xml") == -1:
            if AdditionalCrabInput is None:
                AdditionalCrabInput=tmpl+"/"+file
            else:
                AdditionalCrabInput+=","+tmpl+"/"+file

    return AdditionalCrabInput

def parseReleaseString(release):
    #split and remove 'CMSSW'
    tokens = release.split('_')[1:]

    output = []
    for t in tokens:
        try:
            output.append(int(t))
        except ValueError:
            output.append(t)
    if len(output) < 4:
        output.append('')
    return tuple(output[:4])

def isNewerThan(release,gitrelease):
    #Checks the orders of two releases. If release2 is not set, it is taken as the current release
    log.output("********** Checking if AutoMaticTopTreeProducer should be CVS/Git based ********** " )
    return parseReleaseString(release) >= parseReleaseString(gitrelease)
###################
## OPTION PARSER ##
###################

# Parse the options
optParser = OptionParser()

optParser.add_option("-c", "--cmssw", dest="cmssw_ver",
                  help="Specify which CMSSW you want to use for production (format CMSSW_X_Y_Z)", metavar="")

optParser.add_option("-p", "--cmssw_sample", dest="cmssw_ver_sample",
                  help="Specify which CMSSW branch was used for sample generation/reconstruction (e.g. CMSSW_36X, CMSSW_38X)", metavar="")

optParser.add_option("-d", "--dataset", dest="dataset",
                  help="Specify which dataset you want to process (format /X/YZ)", metavar="")

optParser.add_option("-g","--globaltag", dest="GlobalTag",default="AUTO",
                     help="Specify the GlobalTag", metavar="")

optParser.add_option("-t","--datatier", dest="DataTier",default="NOTFILLED",
                     help="Specify the DataTier of the DataSet (mandatory for datasets ending in /USER", metavar="")

optParser.add_option("-r","--runselection", dest="RunSelection",default="",
                     help="Apply a runselection for this production", metavar="")

optParser.add_option("","--dbsInst", dest="dbsInst",default="",
                     help="Specify the DBSInstance to perform DBS queries", metavar="")

optParser.add_option("","--ce-blacklist", dest="CEBlacklist",default="",
                     help="Specify a comma-separated list of CE's to blacklist IN CRAB", metavar="")

optParser.add_option("","--start-from-pat", action="store_true", dest="startFromPat",default=bool(False),
                     help="Use this flag to start from a previously published PAT sample, provide the sample na me trough -d", metavar="")

optParser.add_option("","--start-from-pat-mc", action="store_true", dest="startFromPatMC",default=bool(False),
                     help="Use this flag to start from a previously published PAT MC sample, provide the sample na me trough -d", metavar="")

optParser.add_option("","--dont-store-pat", action="store_true", dest="DontStorePAT",default=bool(False),
                     help="When this flag is used, the script will submit one job for PAT+TOPTREE and the PAT tuple will NOT be stored on storage.", metavar="")

optParser.add_option("","--addGenEvent", action="store_true", dest="doGenEvent",default=bool(False),
                     help="Use this flag to add GenEvent into PAT and TopTree (WARNING: for ttbar MC only)", metavar="")

optParser.add_option("","--flavourHistoryFilterPath", dest="flavourHistoryFilterPath",default=int(-1),
                     help="Use this option to select a flavour filter history filter path (Default: no filter)", metavar="")

optParser.add_option("","--pbs-submit", action="store_true", dest="doPBS",default=bool(False),
                     help="Submit CRAB jobs to localGrid (Your dataset should be at T2_BE_IIHE)", metavar="")

optParser.add_option("","--dry-run", action="store_true", dest="dryRun",default=bool(False),
                     help="Perform a Dry Run (e.g.: no real submission)", metavar="")

optParser.add_option("","--log-stdout", action="store_true", dest="stdout",default=bool(False),
                     help="Write output to stdout and not to logs/log-*.txt", metavar="")

optParser.add_option("","--forceStandAloneCRAB", action="store_true", dest="forceStandAlone",default=bool(False),
                     help="Force standalone submission whatever the sample size (use at own risk)", metavar="")

optParser.add_option("-l","--setLogFile", dest="logFile",default="EMPTY",
                     help="Choose your own log file name", metavar="")

#optParser.add_option("","--hltMenu", action="store", dest="hltName",default="HLT",
#                     help="Use this option to change the HLT menu name e.g. HLT8E29", metavar="")


(options, args) = optParser.parse_args()

if options.cmssw_ver == None:
    optParser.error("Please specify a CMSSW version.\n")

if options.cmssw_ver_sample == None:
    optParser.error("Please specify a CMSSW version that was used to produce the sample.\n")

if options.dataset == None:
    optParser.error("Please specify a dataset name.\n")


######################
## SOME DEFINITIONS ##
######################

timestamp = strftime("%d%m%Y_%H%M%S")

logFileName = "logs/log-"+options.dataset.split("/")[1]+"-"+options.dataset.split("/")[2]+timestamp+".txt"

if not options.logFile == "EMPTY":
    logFileName = options.logFile
    
TopTreeProducerDir = "/src/TopBrussels/TopTreeProducer/test/"

PatDir = "/src/PhysicsTools/PatAlgos/test/"

dataType = "" # to know if it is MC or data

workingDir = ""

patPublishName = "/a/b/c"

patEventContent = ""

ttreeEventContent = ""

CrabJSON = ""

dbsInst = options.dbsInst

nEventsDBS=int(0)

nEventsPAT=int(0)

nEventsTT=int(0)

jobEffPat=float(0)

jobEffTT=float(0)

doDry=options.dryRun

if options.startFromPatMC:

    options.startFromPat=bool(True)

doStartFromPAT=options.startFromPat

doPBS=options.doPBS

topTreeLocation=""

patLocation=""

patCffName=""

topCffName=""

#####################

################
## LOG SYSTEM ##
################

## provide the desired logfile name to logHandler
## if you provide an empty string the output will be written on the stdOut

if not options.stdout:
    log = logHandler(logFileName)
else:
    log = logHandler("")

#store datasetname for error-messages
log.setDataSet(options.dataset)

if not doDry:
    log.sendErrorMails=bool(True)

##################
## MAIN ROUTINE ##
##################
log.output("------------------------------------")
log.output("--> Automated TopTree production <--")
log.output("------------------------------------")

checkCommandLineOptions(options)

#the CMMSW version comes as CMSSW_X_Y_Z--tag
toptreerelease = options.cmssw_ver.split("--")
#top tree tag
toptreeTag = ""
#cmsswRelease = ""
cmsswRelease = toptreerelease[0]
#Make a boolean  that returns true when the release is a version more recent than CMSSW_5_3_12_patch2 to define the difference between CVS and git
isnew = isNewerThan(cmsswRelease,'CMSSW_5_3_12_patch2')


if isnew:
   log.output(" ---> new release")
   toptreeTag = toptreerelease[1]
   cmsswRelease = toptreerelease[0]
   log.output("--> AutoMaticTopTreeProducer is Git based")
   productionrelease = "/home/dhondt/ProductionReleases/"+toptreeTag+"/"+cmsswRelease
else:
   log.output(" ---> old release")
   log.output("--> AutoMaticTopTreeProducer is CVS based")
   productionrelease = "/home/dhondt/AutoMaticTopTreeProducer/"+options.cmssw_ver

doStartupChecks(productionrelease)


setupDirs(productionrelease+"/src")

#print options.DontStorePAT

if not options.DontStorePAT:

    if not doStartFromPAT:

        processPAT(isnew)

        if not doDry:

            updateTopDB("pat");

    processTOPTREE(isnew)

    if not doDry:

        updateTopDB("toptree");

        announceDataSet()

else:

    processPATandTOPTREE(isnew)

    if not doDry:
    
        updateTopDB("pat+toptree")

        announceDataSet()
    
log.output("********* END OF SCRIPT *********")
