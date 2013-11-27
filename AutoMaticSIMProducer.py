## This script will automatically process any given LHE file into a FASTSIM 'AOD' dataset 

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

# import GENFASTSIMProducer class
from GENFASTSIMProducer import GENFASTSIMProducer

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
    
    global setarchitecture
    setarchitecture = ""
		
    log.output("\t\t--> Checking if you have a "+ver+" release.")

    if os.path.isdir(ver):
        log.output("\t\t\t---> Ok, the release is present!")
        cmd = 'cd '+ver+'; cd src; cmsenv'
        if not ver.rfind("CMSSW_5_") == -1:
            log.output("\t\t\t---> CMSSW_5_X_Y release, setting scram arch to slc5_amd64_gcc462")
            setarchitecture = "export SCRAM_ARCH=\"slc5_amd64_gcc462\";"
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    else:
        log.output("\t\t\t---> ERROR: Please scram the proper release first! (Exiting)")
        dieOnError("Environment: requested CMSSW version is not found in the working directory")

    if type == "gen":

        log.output("\t\t--> Checking if "+ver+" contains Configuration/GenProduction/python/EightTeV/")

        if os.path.isdir(ver+"/src/Configuration/GenProduction/python/EightTeV/"):
            log.output("\t\t\t---> Ok, the directory exists!")
        else:
            log.output("\t\t\t---> ERROR: Please ensure that you have Configuration/GenProduction/python/EightTeV/ checked out! (Exiting)")
            dieOnError("Environment: requested CMSSW version does not contain Configuration/GenProduction/python/EightTeV/")

        log.output("\t\t--> Checking if Configuration/GenProduction/python/EightTeV/ contains the requested config template: "+options.configfile)

        if os.path.exists(ver+"/src/Configuration/GenProduction/python/EightTeV/"+options.configfile):
            log.output("\t\t\t---> Ok, the file exists!")
        else:
            log.output("\t\t\t---> ERROR: Please ensure that you place "+options.configfile+" inside Configuration/GenProduction/python/EightTeV/! (Exiting)")
            dieOnError("Environment: requested config template "+options.configfile+" not found in Configuration/GenProduction/python/EightTeV/")

def checkGT(gt):

    log.output("\t\t--> Checking the GlobalTag")

    if gt == "" or gt.rfind("::All") == -1:
        log.output("\t\t\t---> ERROR: Please ensure that you have provided a proper global tag! (Exiting)")
        dieOnError("Environment: requested global tag "+gt+" is not of the right format")
    else:
        log.output("\t\t\t---> Ok, "+gt+" is a valid GlobalTag!")
        
def inputSummary(productionrelease):

    global log
    global options

    global cmssw_sim
    global gt_sim
    global publish_sim

    global cmssw_toptree
    global gt_toptree

    log.output("----> Summary of input values <----")

    if not cmssw_sim == "":

        if not options.nEvents == -1:
            log.output("\t* GEN-FASTSIM <-> CMSSW: "+productionrelease+" <-> GlobalTag: "+gt_sim+" <-> Publish As: "+publish_sim+" <-> Config Template: "+options.configfile+" <-> #events to process: "+str(options.nEvents)+" <-> sending announcement to "+options.email+" *")
        else:
            log.output("\t* GEN-FASTSIM <-> CMSSW: "+productionrelease+" <-> GlobalTag: "+gt_sim+" <-> Publish As: "+publish_sim+" <-> Config Template: "+options.configfile+" <-> #events to process: all <-> sending announcement to "+options.email+" *")

        checkCMSSW(productionrelease,"gen")

        checkGT(gt_sim)
        
        if not cmssw_toptree == "":
            log.output("\t* PAT-TOPTREE <-> CMSSW: "+cmssw_toptree+" <-> GlobalTag: "+gt_toptree+" *")
            
            checkCMSSW(cmssw_toptree,"")
            
            checkGT(gt_toptree)

def processGENFASTSIM():

    log.output(" ----> Preparing to produce the GEN-FASTSIM sample <----")

    startTime = gmtime()

    global workingDir_sim
    global doDry
    global options

    global cmssw_sim
    global gt_sim
    global publish_sim

    global GENFASTSIM_CFFPath
    global GENFASTSIM_PublishName
    global GENFASTSIM_nEvents
    global GENFASTSIM_PNFSLocation
    global GENFASTSIM_jobEff
    global GENFASTSIM_LHEFiles

    sim = GENFASTSIMProducer(timestamp,workingDir_sim,log,setarchitecture)
 
    sim.createConfig(publish_sim,options.configfile,gt_sim,options.lhedir,options.nEvents,options.campaign)

    crab = CRABHandler(timestamp,workingDir_sim,log)

    if options.nEvents == "-1" or int(options.nEvents) > int(sim.getNLHEevents()):
        options.nEvents = sim.getNLHEevents()

    crab.nEvents = str(options.nEvents)

    if not str(options.nEvents) == "-1" and int(options.nEvents) < 500:
        crab.nEventsPerJob=crab.nEvents
    else:
        crab.nEventsPerJob = "500"

    crab.AdditionalCrabInput = sim.getlhefiles()

    crab.createCRABcfg("crab_genfastsim_"+timestamp+".cfg",
                   publish_sim+"_"+options.campaign,
                   sim.getConfigFileName(),
                   sim.getOutputFileName(),
                   "GENFASTSIM",
                   bool(True),
                   "",
                   "",
                   bool(False))
    #the 'publish' argument set to bool(False) does not work yet, crabhandler encounters a problem because it wants to split "None" (the dataset when doing GEN-FASTSIM) into several pieces divided by "/" (as in a normal DAS dataset)...
    
    crab.setForceWhiteList(bool(True))

    if not doDry:
        
        crab.submitJobs()

        nEventsDBS = crab.getnEventsDBS()

        ##for testing
        #crab.idleTime = int(60)
        #crab.idleTimeResubmit = int(120)
        
        crab.checkJobs()
        
        time.sleep(60) # to be sure the jobs are in done status

        GENFASTSIM_CFFPath = workingDir_sim+"/"+sim.getConfigFileName()

        GENFASTSIM_LHEFiles = sim.getlhefiles()
        
        GENFASTSIM_PublishName = crab.publishDataSet()

        GENFASTSIM_nEvents = crab.checkFJR()

        GENFASTSIM_PNFSLocation = crab.getOutputLocation()

        GENFASTSIM_jobEff = crab.getJobEff()
				
				#remove sandbox (lhe files are compressed, but can be sizable when you have a lot of lhe files and tasks: better clean up when a task is done)
        log.output("--> Removing task sandbox ")
        Popen('rm '+workingDir_sim+'/'+crab.UIWorkingDir+'/share/*.tgz', shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
        #remove lhe files in crab directory if they were copied when the lhe files in the original lhe directory were gzipped
        log.output("--> Removing local copied LHE files in directory for crab")
        Popen('rm '+workingDir_sim+'/*.lhe', shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
				
        log.output("--> Job Efficiency: "+str(GENFASTSIM_jobEff))

    endTime = gmtime()

    log.output("--> The GEN-FASTSIM production took "+ str((time.mktime(endTime)-time.mktime(startTime))/3600.0)+" hours.")

    log.appendToMSG("\n* GEN-FASTSIM production information: ")
    
    if not crab.getOutputLocation() == "":

        log.appendToMSG("\n\t-> Data location: "+GENFASTSIM_PNFSLocation+"\n")

    log.appendToMSG("\t-> DataSet was published in DBS as: "+GENFASTSIM_PublishName)
        
    log.appendToMSG("\t-> Number of events processed: "+str(GENFASTSIM_nEvents))

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
		
    #mail.toAnnounce = [ "gvonsem@vub.ac.be" ]
    #mail.toError = [ "gvonsem@vub.ac.be" ]
    
    log.output("--> sending to "+options.email)
    mail.toAnnounce = [ str(options.email) ]
    mail.toError = [ str(options.email) ]

    type = "announcement"

    subject = "New fast simulation production"

    msg = "Hi,\n"
    msg += "\n"
    msg += "This is an automatically generated e-mail to announce that a GEN-FASTSIM-HLT production is completed."

    msg += log.getAnnouncementMSG()

    msg += "\n\nMore information on this production can be found on https://mtop.iihe.ac.be/TopDB."

    msg += "\n\n\nCheers,\nThe GEN-FASTSIMProduction team"
   
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
    global GENFASTSIM_CFFPath
    global GENFASTSIM_PublishName
    global GENFASTSIM_nEvents
    global GENFASTSIM_PNFSLocation
    global GENFASTSIM_jobEff
    global GENFASTSIM_LHEFiles
    
    db = topDBInterface()

    # get current dir

    cmd ='pwd'
    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    dir = pExe.stdout.read()

    ## insert GENFASTSIM into topDB
    print GENFASTSIM_jobEff
    if type == "GENFASTSIM":
        print GENFASTSIM_PublishName
        db.insertGENFASTSIM("TopTree Producer",GENFASTSIM_PublishName.split("\n")[0],GENFASTSIM_PNFSLocation,cmssw_sim,gt_sim,GENFASTSIM_CFFPath,GENFASTSIM_LHEFiles,GENFASTSIM_jobEff,GENFASTSIM_nEvents,options.campaign)
		    #insert dataset into topDB
        cmssw_dataset = "CMSSW_53X"
        if not cmssw_sim.rfind("CMSSW_5_2") == -1:
            cmssw_dataset = "CMSSW_52X"						
        elif not cmssw_sim.rfind("CMSSW_5_3") == -1:
            cmssw_dataset = "CMSSW_53X"
        else:
            log.output("--> WARNING: CMSSW version not recognized in database; dataset will be inserted in TopDB as CMSSW_53X!") 
				
        db.insertDataSet("TopTree Producer",GENFASTSIM_PublishName.split("\n")[0],"NewPhysics","1",cmssw_dataset,"AOD","Produced")
		
###################
## OPTION PARSER ##
###################

# Parse the options
optParser = OptionParser()

optParser.add_option("-c", "--cmssw", dest="cmssw_ver",
                  help="Specify which CMSSW releases you want to use for GEN-FASTSIM and TopTree (separated by ',')", metavar="")

optParser.add_option("-g","--globaltag", dest="GlobalTag",
                     help="Specify which GlobalTags you want to use for GEN-FASTSIM and TopTree (separated by ',')", metavar="")

optParser.add_option("-f","--configfile", dest="configfile",
                     help="Specify the config template filename inside Configuration/GenProduction/python/EightTeV you want to use for GEN-FASTSIM. ", metavar="")

optParser.add_option("-d","--lhedir", dest="lhedir",
                     help="Specify the directory containing your LHE files for GEN-FASTSIM. ", metavar="")

optParser.add_option("-p", "--publish-name", dest="publish",
                  help="Specify the DAS publication name for the GEN-FASTSIM", metavar="")

optParser.add_option("-a", "--campaign", dest="campaign",default="Summer12",
                  help="Specify the name of the production campaign (e.g.: Summer12,...)", metavar="")

optParser.add_option("-n","--nevents", dest="nEvents",default=-1,
                     help="Process only N events. ", metavar="")

optParser.add_option("","--dry-run", action="store_true", dest="dryRun",default=bool(False),
                     help="Perform a Dry Run (e.g.: no real submission)", metavar="")

optParser.add_option("","--log-stdout", action="store_true", dest="stdout",default=bool(False),
                     help="Write output to stdout and not to logs/log-*.txt", metavar="")

optParser.add_option("-l","--setLogFile", dest="logFile",default="EMPTY",
                     help="Choose your own log file name", metavar="")

optParser.add_option("","--email", dest="email",default="gvonsem@vub.ac.be",
                     help="Change the email address for announcement from GEN-FASTSIM datasets to another email (default = gvonsem@vub.ac.be)", metavar="")

(options, args) = optParser.parse_args()

if options.cmssw_ver == None:
    optParser.error("Please specify at least one CMSSW version.\n")

if options.GlobalTag == None:
    optParser.error("Please specify at least one GlobalTag. \n")

if options.publish == None:
    optParser.error("Please specify the DAS PublishName. \n")

if options.configfile == None:
    optParser.error("Please specify the config template filename for GEN-FASTSIM. \n")

if options.lhedir == None:
    optParser.error("Please specify a directory containing your LHE files for GEN-FASTSIM. \n")

#check if LHE directory exists as full path
if not (os.path.exists(options.lhedir) and os.path.isabs(options.lhedir)):
    optParser.error("The specified directory with LHE files does not exist. Please specify a directory as full path on the user disk. \n")


######################
## SOME DEFINITIONS ##
######################

timestamp = strftime("%d%m%Y_%H%M%S")

logFileName = "logs/log-"+(options.publish.split(","))[0]+"-"+timestamp+".txt"

if not options.logFile == "EMPTY":
    logFileName = options.logFile
    
workingDir_sim = ""

doDry=options.dryRun

# CMSSW Versions #

cmssw = options.cmssw_ver.split(",")

cmssw_sim = cmssw[0]
cmssw_toptree = ""

if len(cmssw) > 1:
    cmssw_toptree = cmssw[1]
    
# GlobalTags #

gt = options.GlobalTag.split(",")

gt_sim = gt[0]
gt_toptree = ""

if len(gt) > 1:
    gt_toptree = gt[1]
    
# publish names #

publish = options.publish.split(",")

publish_sim = publish[0]
    
#####################

#####################################
## CONTAINERS TO STORE INFO FOR DB ##
#####################################

#GEN-FASTSIM
GENFASTSIM_CFFPath = ""
GENFASTSIM_PublishName = "/a/b/c"
GENFASTSIM_nEvents = ""
GENFASTSIM_PNFSLocation = ""
GENFASTSIM_jobEff = ""
GENFASTSIM_LHEFiles = ""

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

#if not doDry:
#    log.sendErrorMails=bool(True) # FIXME

##################
## MAIN ROUTINE ##
##################
    
log.output("--------------------------------------------")
log.output("--> Automated FAST SIMULATION production <--")
log.output("--------------------------------------------")

simrelease = cmssw_sim.split("--")
productionrelease ="/home/dhondt/ProductionReleases/"+simrelease[1]+"/"+simrelease[0]

# display input options and do consistency checks
inputSummary(productionrelease)

# check GRID proxy

crab = CRABHandler("","",log)

crab.checkGridProxy(False)

crab.checkCredentials(False)

# create working directories
if not cmssw_sim == "":


    workingDir_sim = setupDirs(productionrelease+"/src","GEN-FASTSIM_"+publish_sim)

processGENFASTSIM()

if not options.dryRun:
    updateTopDB("GENFASTSIM")

if not doDry:
    
    announceDataSet()

log.output("********* END OF SCRIPT *********")
