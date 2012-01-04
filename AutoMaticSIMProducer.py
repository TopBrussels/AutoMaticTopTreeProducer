## This script will automatically process any given LHE file into a GEN-SIM-DIGI and RECO dataset

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

# import logHandler
from logHandler import logHandler

# import mailHandler
from MailHandler import MailHandler

# import interface to topDB
from sqlHandler import topDBInterface

# import GENSIMProducer class
from GENSIMProducer import GENSIMProducer

# import RECOProducer class
from RECOProducer import RECOProducer

################################
## PLACE TO PUT THE FUNCTIONS ##
################################

def dieOnError(string):

    global doDry
    global log

    if doDry:

        log.dieOnError(string)

    else:

        log.dieOnError(string)

def setupDirs(baseDir,publish):

    dir = []

    dir.append(baseDir+"/SIMConfigurationFiles")


    dir.append(dir[len(dir)-1]+"/"+publish)

    dir.append(dir[len(dir)-1]+"/"+timestamp)
    
    for i in range(0,len(dir)):

        if not os.path.exists(dir[i]):

            log.output("\t--> Creating directory: ./"+dir[i])

            os.makedirs(dir[i])

    return dir[len(dir)-1]

def checkCMSSW(ver,type):

    log.output("\t\t--> Checking if you have a "+ver+" release.")

    if os.path.isdir(ver):
        log.output("\t\t\t---> Ok, the release is present!")
        cmd ='cd '+options.cmssw_ver+'; cmsenv'
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    else:
        log.output("\t\t\t---> ERROR: Please scram the proper release first! (Exiting)")
        dieOnError("Environment: resquested CMSSW version is not found in the working directory")

    if type == "gen":

        log.output("\t\t--> Checking if "+ver+" contains Configuration/GenProduction/python/")

        if os.path.isdir(ver+"/src/Configuration/GenProduction/python/"):
            log.output("\t\t\t---> Ok, the directory exists!")
        else:
            log.output("\t\t\t---> ERROR: Please ensure that you have Configuration/GenProduction/python/ checked out! (Exiting)")
            dieOnError("Environment: resquested CMSSW version does not contain Configuration/GenProduction/python/")

        log.output("\t\t--> Checking if Configuration/GenProduction/python/ contains the requested config template: "+options.configfile)

        if os.path.exists(ver+"/src/Configuration/GenProduction/python/"+options.configfile):
            log.output("\t\t\t---> Ok, the file exists!")
        else:
            log.output("\t\t\t---> ERROR: Please ensure that you place "+options.configfile+" inside Configuration/GenProduction/python/! (Exiting)")
            dieOnError("Environment: resquested config template "+options.configfile+" not found in Configuration/GenProduction/python/")

def checkGT(gt):

    log.output("\t\t--> Checking the GlobalTag")

    if gt == "" or gt.rfind("::All") == -1:
        log.output("\t\t\t---> ERROR: Please ensure that you have provided a proper global tag! (Exiting)")
        dieOnError("Environment: resquested global tag "+gt+" is not of the right format")
    else:
        log.output("\t\t\t---> Ok, "+gt+" is a valid GlobalTag!")
        
def inputSummary():

    global log
    global options

    global cmssw_sim
    global gt_sim
    global publish_sim

    global cmssw_rec
    global gt_rec
    global publish_rec

    global cmssw_toptree
    global gt_toptree

    log.output("----> Summary of input values <----")

    if not cmssw_sim == "":

        if not options.nEvents == -1:
            log.output("\t* GEN-SIM <-> CMSSW: "+cmssw_sim+" <-> GlobalTag: "+gt_sim+" <-> Publish As: "+publish_sim+" <-> Config Template: "+options.configfile+" <-> #events to process: "+str(options.nEvents)+" *")
        else:
            log.output("\t* GEN-SIM <-> CMSSW: "+cmssw_sim+" <-> GlobalTag: "+gt_sim+" <-> Publish As: "+publish_sim+" <-> Config Template: "+options.configfile+" <-> #events to process: all *")

        checkCMSSW(cmssw_sim,"gen")

        checkGT(gt_sim)
                   
    if not options.skipreco:
        log.output("\t* DIGI-RECO <-> CMSSW: "+cmssw_rec+" <-> GlobalTag: "+gt_rec+" <-> Publish As: "+publish_rec+" *")
        
        checkCMSSW(cmssw_rec,"")
        
        checkGT(gt_rec)
        
        if not cmssw_toptree == "":
            log.output("\t* PAT-TOPTREE <-> CMSSW: "+cmssw_toptree+" <-> GlobalTag: "+gt_toptree+" *")
            
            checkCMSSW(cmssw_toptree,"")
            
            checkGT(gt_toptree)

def processGENSIM():

    log.output(" ----> Preparing to produce the GEN-SIM sample <----")

    startTime = gmtime()

    global workingDir_sim
    global doDry
    global options

    global cmssw_sim
    global gt_sim
    global publish_sim

    global GENSIM_CFFPath
    global GENSIM_PublishName
    global GENSIM_nEvents
    global GENSIM_PNFSLocation
    global GENSIM_jobEff
    global GENSIM_LHEFiles

    sim = GENSIMProducer(timestamp,workingDir_sim,log)
 
    sim.createConfig(publish_sim,options.configfile,gt_sim,options.lhedir,options.nEvents)

    crab = CRABHandler(timestamp,workingDir_sim,log)

    if options.nEvents == -1 or int(options.nEvents) > int(sim.getNLHEevents()):
        options.nEvents = sim.getNLHEevents()

    crab.nEvents = str(options.nEvents)

    if not str(options.nEvents) == "-1" and int(options.nEvents) < 500:
        crab.nEventsPerJob=crab.nEvents
    else:
        crab.nEventsPerJob = "500"

    crab.AdditionalCrabInput = sim.getlhefiles()

    crab.createCRABcfg("crab_gensim_"+timestamp+".cfg",
                   publish_sim+"_"+options.campaign+"_"+timestamp,
                   sim.getConfigFileName(),
                   sim.getOutputFileName(),
                   "GENSIM",
                   bool(True),
                   "",
                   "",
                   bool(False))

    crab.setForceWhiteList(bool(True))

    if not doDry:
        
        crab.submitJobs()

        nEventsDBS = crab.getnEventsDBS()

        #crab.idleTime = int(60)
        #crab.idleTimeResubmit = int(120)
        
        crab.checkJobs()
        
        time.sleep(60) # to be shure the jobs are in done status

        GENSIM_CFFPath = workingDir_sim+"/"+sim.getConfigFileName()

        GENSIM_LHEFiles = sim.getlhefiles()
        
        GENSIM_PublishName = crab.publishDataSet()

        GENSIM_nEvents = crab.checkFJR()

        GENSIM_PNFSLocation = crab.getOutputLocation()

        GENSIM_jobEff = crab.getJobEff()

        log.output("--> Job Efficiency: "+str(GENSIM_jobEff))

    endTime = gmtime()

    log.output("--> The GEN-SIM production took "+ str((time.mktime(endTime)-time.mktime(startTime))/3600.0)+" hours.")

    log.appendToMSG("\n* GEN-SIM production information: ")
    
    if not crab.getOutputLocation() == "":

        log.appendToMSG("\n\t-> Data location: "+GENSIM_PNFSLocation+"\n")

    log.appendToMSG("\t-> DataSet was published in DBS as: "+GENSIM_PublishName)
        
    log.appendToMSG("\t-> Number of events processed: "+str(GENSIM_nEvents))


def processRECO():

    log.output(" ----> Preparing to produce the RECO sample <----")

    startTime = gmtime()

    global workingDir_rec
    global doDry
    global options

    global cmssw_rec
    global gt_rec
    global publish_rec

    global RECO_GENSrc
    global RECO_CFFPath
    global RECO_PublishName
    global RECO_nEvents
    global RECO_PNFSLocation
    global RECO_jobEff
    global RECO_SIMDataset

    rec = RECOProducer(timestamp,workingDir_rec,log)
 
    rec.createConfig(options.campaign,gt_rec)

    crab = CRABHandler(timestamp,workingDir_rec,log)
        
    crab.nEvents = "-1" #str(options.nEvents)
    crab.nEventsPerJob = "500"

    crab.setDBSInst(options.dbsInst)

    if options.startFromSim == None:
        crab.createCRABcfg("crab_reco_"+timestamp+".cfg",
                           GENSIM_PublishName,
                           rec.getConfigFileName(),
                           rec.getOutputFileName(),
                           "RECO",
                           bool(True),
                           "",
                           "",
                           bool(False))
        RECO_SIMDataset = GENSIM_PublishName
    else:
        crab.createCRABcfg("crab_reco_"+timestamp+".cfg",
                           options.startFromSim,
                           rec.getConfigFileName(),
                           rec.getOutputFileName(),
                           "RECO",
                           bool(True),
                           "",
                           "",
                           bool(False))
        RECO_SIMDataset = options.startFromSim
    
    if not doDry:
        
        crab.submitJobs()

        nEventsDBS = crab.getnEventsDBS()

        #crab.idleTime = int(60)
        #crab.idleTimeResubmit = int(120)
        
        crab.checkJobs()
        
        time.sleep(60) # to be shure the jobs are in done status

        RECO_CFFPath = rec.getConfigFileName()
        
        RECO_PublishName = crab.publishDataSet()

        RECO_nEvents = crab.checkFJR()

        RECO_PNFSLocation = crab.getOutputLocation()

        RECO_jobEff = crab.getJobEff()

        log.output("--> Job Efficiency: "+str(RECO_jobEff))

    endTime = gmtime()

    log.output("--> The RECO production took "+ str((time.mktime(endTime)-time.mktime(startTime))/3600.0)+" hours.")

    log.appendToMSG("\n* RECO production information: ")

    if options.startFromSim == None:

        log.appendToMSG("\n\t-> GEN-SIM Dataset: "+GENSIM_PublishName+"\n")
    else:
        log.appendToMSG("\n\t-> GEN-SIM Dataset: "+options.startFromSim+"\n")

    if not crab.getOutputLocation() == "":

        log.appendToMSG("\n\t-> Data location: "+RECO_PNFSLocation+"\n")

    log.appendToMSG("\t-> DataSet was published in DBS as: "+RECO_PublishName)
        
    log.appendToMSG("\t-> Number of events processed: "+str(RECO_nEvents))

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

    subject = "New simulation production"

    msg = "Dear top quark group,\n"
    msg += "\n"
    msg += "This is an automatically generated e-mail to announce that a GEN-SIM/DIGI-RECO production is completed."

    msg += log.getAnnouncementMSG()

    msg += "\n\nMore information on this production can be found on https://mtop.iihe.ac.be/TopDB."

    msg += "\n\n\nCheers,\nThe GEN-SIM-DIGI-RECOProduction team"
   
    mail.sendMail(type,subject,msg)



##############################
## TOPDB DATABASE INTERFACE ##
##############################

def updateTopDB(type): # type = pat or toptree

    log.output("********** Adding the information to TopDB **********")

    ## SIM INFO
    global cmssw_sim
    global gt_sim
    global publish_sim
    global GENSIM_CFFPath
    global GENSIM_PublishName
    global GENSIM_nEvents
    global GENSIM_PNFSLocation
    global GENSIM_jobEff
    global GENSIM_LHEFiles
    
    db = topDBInterface()

    # get current dir

    cmd ='pwd'
    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    dir = pExe.stdout.read()

    ## insert GENSIM into topDB

    if type == "GENSIM":

        db.insertGENSIM("TopTree Producer",GENSIM_PublishName,GENSIM_PNFSLocation,cmssw_sim,gt_sim,GENSIM_CFFPath,GENSIM_LHEFiles,GENSIM_jobEff,GENSIM_nEvents,options.campaign)

    elif type == "RECO":

        db.insertRECO("TopTree Producer",RECO_SIMDataset,RECO_PublishName,RECO_PNFSLocation,cmssw_rec,gt_rec,RECO_CFFPath,RECO_jobEff,RECO_nEvents,options.campaign)
    
###################
## OPTION PARSER ##
###################

# Parse the options
optParser = OptionParser()

optParser.add_option("-c", "--cmssw", dest="cmssw_ver",
                  help="Specify which CMSSW releases you want to use for GEN-SIM, DIGI-RECO and TopTree (separated by ',')", metavar="")

optParser.add_option("-g","--globaltag", dest="GlobalTag",
                     help="Specify which GlobalTags you want to use for GEN-SIM, DIGI-RECO and TopTree (separated by ',')", metavar="")

optParser.add_option("-f","--configfile", dest="configfile",
                     help="Specify the config template filename inside Configuration/GenProduction/python/ you want to use for GEN-SIM. ", metavar="")

optParser.add_option("-d","--lhedir", dest="lhedir",
                     help="Specify the directory containing your LHE files for GEN-SIM. ", metavar="")

optParser.add_option("-p", "--publish-name", dest="publish",
                  help="Specify the DAS publication name for the GEN-SIM and DIGI-RECO step (separated by ',')", metavar="")

optParser.add_option("-a", "--campaign", dest="campaign",default="Summer11",
                  help="Specify the name of the production campaign (e.g.: Summer11,Fall11,....)", metavar="")

optParser.add_option("-r", "--start-from-produced-sim", dest="startFromSim",
                  help="Specify DAS dataset name of the GEN-SIM dataset you want to DIGI-RECO", metavar="")

optParser.add_option("-s", "--skip-reco", action="store_true", dest="skipreco",default=bool(False),
                  help="Use this flag to perform the GEN-SIM step only", metavar="")

optParser.add_option("-n","--nevents", dest="nEvents",default=-1,
                     help="Process only N events. ", metavar="")

optParser.add_option("","--dbsInst", dest="dbsInst",default="cms_dbs_ph_analysis_02",
                     help="Specify the DBSInstance to perform DBS queries for RECO step", metavar="")

optParser.add_option("","--dry-run", action="store_true", dest="dryRun",default=bool(False),
                     help="Perform a Dry Run (e.g.: no real submission)", metavar="")

optParser.add_option("","--log-stdout", action="store_true", dest="stdout",default=bool(False),
                     help="Write output to stdout and not to logs/log-*.txt", metavar="")

optParser.add_option("-l","--setLogFile", dest="logFile",default="EMPTY",
                     help="Choose your own log file name", metavar="")


(options, args) = optParser.parse_args()

if options.cmssw_ver == None:
    optParser.error("Please specify at least one CMSSW version.\n")

if options.GlobalTag == None:
    optParser.error("Please specify at least one GlobalTag. \n")

if options.publish == None:
    optParser.error("Please specify at least one DAS PublishName. \n")

if options.configfile == None and options.startFromSim == None:
    optParser.error("Please specify the config template filename for GEN-SIM. \n")

if options.lhedir == None and options.startFromSim == None:
    optParser.error("Please specify the directory containing your LHE files for GEN-SIM. \n")

if not len(options.publish.split(",")) == 2 and options.startFromSim == None and not options.skipreco:
    optParser.error("Please specify two DAS PublishNames when running both GEN-SIM and DIGI-RECO. \n")


######################
## SOME DEFINITIONS ##
######################

timestamp = strftime("%d%m%Y_%H%M%S")

logFileName = "logs/log-"+(options.publish.split(","))[0]+"-"+timestamp+".txt"

if not options.logFile == "EMPTY":
    logFileName = options.logFile
    
workingDir_sim = ""
workingDir_rec = ""

#dbsInst = options.dbsInst

doDry=options.dryRun

# CMSSW Versions #

cmssw = options.cmssw_ver.split(",")

cmssw_sim = cmssw[0]
cmssw_rec = ""
cmssw_toptree = ""

if len(cmssw) > 1:
    cmssw_rec = cmssw[1]
if len(cmssw) > 2:
    cmssw_toptree = cmssw[2]

if not options.startFromSim == None:
    cmssw_toptree = cmssw_rec
    cmssw_rec = cmssw_sim
    cmssw_sim = ""
    
# GlobalTags #

gt = options.GlobalTag.split(",")

gt_sim = gt[0]
gt_rec = ""
gt_toptree = ""

if len(gt) > 1:
    gt_rec = gt[1]
if len(cmssw) > 2:
    gt_toptree = gt[2]

if not options.startFromSim == None:
    gt_toptree = gt_rec
    gt_rec = gt_sim
    gt_sim = ""
    
# publish names #

publish = options.publish.split(",")

publish_sim = publish[0]

if options.startFromSim == None and not options.skipreco:
    publish_rec = publish[1]
else:
    publish_rec = publish_sim
    #publish_sim = ""
    
#####################

#####################################
## CONTAINERS TO STORE INFO FOR DB ##
#####################################

#GEN-SIM
GENSIM_CFFPath = ""
GENSIM_PublishName = "/a/b/c"
GENSIM_nEvents = ""
GENSIM_PNFSLocation = ""
GENSIM_jobEff = ""
GENSIM_LHEFiles = ""

#RECO
RECO_GENSrc = ""
RECO_CFFPath = ""
RECO_PublishName = ""
RECO_nEvents = ""
RECO_PNFSLocation = ""
RECO_jobEff = ""
RECO_SIMDataset = ""

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
log.setDataSet(options.publish)

if not doDry:
    log.sendErrorMails=bool(True) # FIXME

##################
## MAIN ROUTINE ##
##################
    
log.output("---------------------------------------")
log.output("--> Automated SIMULATION production <--")
log.output("---------------------------------------")

# display input options and do consistency checks
inputSummary()

# check GRID proxy

crab = CRABHandler("","",log)

crab.checkGridProxy(False)

crab.checkCredentials(False)

# create working directories
if not cmssw_sim == "":
    workingDir_sim = setupDirs(cmssw_sim+"/src","GEN-SIM_"+publish_sim)
if not cmssw_rec == "" and not options.skipreco:
    workingDir_rec = setupDirs(cmssw_rec+"/src","RECO_"+publish_rec)

# GEN-SIM step

if options.startFromSim == None:

    processGENSIM()

    if not options.dryRun:
        updateTopDB("GENSIM")

if not options.skipreco:
    processRECO()

    if not options.dryRun:
        updateTopDB("RECO")

if not doDry:
    
    announceDataSet()

log.output("********* END OF SCRIPT *********")
