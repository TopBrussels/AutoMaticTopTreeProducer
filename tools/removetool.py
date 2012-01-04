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

# sql interface
from sqlHandler import SQLHandler

# import crabhandler for proxy stuff

from CrabHandler import CRABHandler
from logHandler import logHandler

# get the sensitive information from config file

login=""
password=""
dbaseName=""
dbaseHost=""
        
for line in open("../.config","r"):
    if not line.rfind("DBUser") == -1:
        login = line.split(" ")[1].split("\n")[0]
    elif not line.rfind("DBPass") == -1:
        password = line.split(" ")[1].split("\n")[0]
    elif not line.rfind("DBHost") == -1:
        dbaseHost = line.split(" ")[1].split("\n")[0]
    elif not line.rfind("DBName") == -1:
        dbaseName = line.split(" ")[1].split("\n")[0]
        
sql = SQLHandler(dbaseName,login,password,dbaseHost)


###############
### METHODS ###
###############

def rmSRMdir (dir):

    global srmHost

    if os.path.exists(dir):

        log.output("  ---> Going into directory "+dir)

        for i in os.listdir(dir):
            
            log.output("   ----> Removing file "+i)

            # do the removal

            cmd ='srmrm '+srmHost+dir+'/'+str(i)
            
            pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            out = pExe.stdout.read()

            #print cmd
            
        #log.output("   ----> Removing directory "+dir)

        # do the removal

        splittedDir = dir.split("/")

        #print splittedDir

        max = len(splittedDir)

        for i in range(0,5):

            if max > 7: # do not go under /pnfs/iihe/cms/store/user/USERNAME

                toRemove = "/"

                for j in range(1,max):

                    toRemove += splittedDir[j]+"/"

                #check if it's empty
                
                if not os.listdir(toRemove):

                    log.output("   ----> Removing empty directory "+toRemove)

                    cmd ='srmrmdir '+srmHost+toRemove
            
                    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    out = pExe.stdout.read()

                    #print cmd

                    print out

            max -= 1

def rmTopTree(file):

    if os.path.exists(file):

        log.output("  ---> Removing Merged TopTree file "+file)

        os.remove(file)
        
def rmFromTopDB(table,id):

    log.output("  ---> Removing entry "+str(id)+" from TopDB table "+table)

    sql.createQuery("DELETE",table,"*","id = '"+id+"'")

    sql.execQuery()

def invalDBS(publishname,cmsDir):
    
    new= cmsDir.split("\\n")

    cmsDir = ""
    
    for i in range(0,len(new)):

        cmsDir += new[i]

    new= cmsDir.split("/")

    cmsDir = ""
    
    for i in range(0,len(new)-1):

        cmsDir += new[i]+'/'

    publishname = publishname.split("\\n")[0]

    log.output("  ---> Invalidating sample "+publishname+" in local DBS")

    initEnv = 'cd '+cmsDir+'; eval `scramv1 runtime -sh`; source /user/cmssoft/crab/latest/crab.sh'
    
    cmd = initEnv+'; DBSInvalidateDataset.py --DBSURL=https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet --datasetPath='+publishname
            
    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    out = pExe.stdout.read()
    
    print out
 
#####################
### OPTION PARSER ###
#####################

optParser = OptionParser()

optParser.add_option("","--remove_dataset", dest="rmDataSet",default="None",
                     help="Use this flag to remove the given dataset (note: associated patTuples and TopTrees will be removed", metavar="")

optParser.add_option("","--remove_pat", dest="rmPat",default="None",
                     help="Use this flag to remove the given Pattuple (associated toptrees WILL be removed). As an argument it takes DBS dataset name", metavar="")

optParser.add_option("","--remove_toptree", dest="rmTopTree",default="None",
                     help="Use this flag to remove the given TopTree (the source PAT dataset will NOT be removed). As an argument it takes the DataBase ID of the TopTree", metavar="")

optParser.add_option("","--remove_pat_only", dest="rmPatonly",default="None",
                     help="Use this flag to remove the given Pattuple (associated toptrees will NOT be removed). As an argument it takes DBS dataset name", metavar="")

optParser.add_option("","--assume-yes", action="store_true", dest="assume_yes",default=bool(False),
                     help="Answer yes to all questions", metavar="")

(options, args) = optParser.parse_args()

############
### MAIN ###
############

# settings

srmHost = "srm://maite.iihe.ac.be:8443"

# store some stuff

# dataset to remove

datasetID = ""

# pat to remove

id = []
storagePath = []
dbsPublish = []
CffFilePath = []

# toptree to remove

idTop = []
storagePathTop = []
mergedTopLocation = []

# logging

log = logHandler("")

# update grid-proxy for srm commands

crab = CRABHandler("","",log)

crab.checkGridProxy(False)

#### Remove DataSet -> ALL associated PatTuples -> All associated TopTrees

if not options.rmDataSet == "None":

    log.output("--> Removing dataset "+options.rmDataSet+" and all associated PATtuples and TopTrees")

    sql.createQuery("SELECT","datasets","id","name = '"+options.rmDataSet+"'")

    result = sql.execQuery().split('\n')

    if len(result) == 1:

        log.output(" ---> RRROR: DataSet was not found in TopDB")

        sys.exit(1)

    else:

        datasetID = result[1]

        log.output("--> Rertrieving information for PatTuples and TopTrees to be removed")

        sql.createQuery("SELECT","patuples","id,StoragePath,name,CffFilePath","dataset_id = '"+datasetID+"'")

        result = sql.execQuery().split('\n')

        if len(result) > 1:

            for i in range(1,len(result)-1):

                id.append(result[i].split("\t")[0])
                storagePath.append(result[i].split("\t")[1])
                dbsPublish.append(result[i].split("\t")[2])
                CffFilePath.append(result[i].split("\t")[3])


                #log.output("  ----> Removing PATtuple with ID "+str(id[len(id)-1])+" at "+storagePath[len(storagePath)-1])

                #log.output("   -----> Looking for associated TopTrees")

                sql.createQuery("SELECT","toptrees","id,StoragePath,TopTreeLocation","patuple_id = '"+id[len(id)-1].split("\\n")[0]+"'")

                result2 = sql.execQuery().split('\n')

                if len(result2) > 1:

                    for j in range(1,len(result2)-1):

                        idTop.append(result2[j].split("\t")[0])
                        storagePathTop.append(result2[j].split("\t")[1])
                        mergedTopLocation.append(result2[j].split("\t")[2])

                        #log.output("    ------> Removing TopTree with ID "+str(id[len(id)-1])+" at "+storagePath[len(storagePath)-1])

## remove only a toptree

if not options.rmTopTree == "None":

    log.output("--> Removing TopTree "+options.rmTopTree)

    sql.createQuery("SELECT","toptrees","id,StoragePath,TopTreeLocation","id = '"+options.rmTopTree+"'")

    result = sql.execQuery().split('\n')

    if len(result) == 1:

        log.output(" ---> ERROR: TopTree was not found in TopDB")

        sys.exit(1)

    else:

        idTop.append(result[1].split("\t")[0])
        storagePathTop.append(result[1].split("\t")[1])
        mergedTopLocation.append(result[1].split("\t")[2])

## remove only a pattuple

if not options.rmPatonly == "None":

    log.output("--> Removing Pattuple "+options.rmPatonly)

    sql.createQuery("SELECT","patuples","id,StoragePath,name,CffFilePath","name REGEXP '"+options.rmPatonly+"'")

    result = sql.execQuery().split('\n')

    if len(result) == 1:

        log.output(" ---> RRROR: PatTuple was not found in TopDB")

        sys.exit(1)

    else:

        id.append(result[1].split("\t")[0])
        storagePath.append(result[1].split("\t")[1])
        dbsPublish.append(result[1].split("\t")[2])
        CffFilePath.append(result[1].split("\t")[3])


## remove a pattuple and associated toptrees

if not options.rmPat == "None":

    log.output("--> Removing Pattuple "+options.rmPat)

    sql.createQuery("SELECT","patuples","id,StoragePath,name,CffFilePath","name REGEXP '"+options.rmPat+"'")
    result = sql.execQuery().split('\n')

    if len(result) == 1:

        log.output(" ---> RRROR: PatTuple was not found in TopDB")

        sys.exit(1)

    else:

        id.append(result[1].split("\t")[0])
        storagePath.append(result[1].split("\t")[1])
        dbsPublish.append(result[1].split("\t")[2])
        CffFilePath.append(result[1].split("\t")[3])

        sql.createQuery("SELECT","toptrees","id,StoragePath,TopTreeLocation","patuple_id = '"+id[len(id)-1].split("\\n")[0]+"'")

        result2 = sql.execQuery().split('\n')

        if len(result2) > 1:

            for j in range(1,len(result2)-1):

                idTop.append(result2[j].split("\t")[0])
                storagePathTop.append(result2[j].split("\t")[1])
                mergedTopLocation.append(result2[j].split("\t")[2])
                
                #log.output("    ------> Removing TopTree with ID "+str(id[len(id)-1])+" at "+storagePath[len(storagePath)-1])

                        


## general removal loop

if len(id) == 0 and len(idTop) == 0 and options.rmDataSet == "None":

    sys.exit()

log.output(" --> The following actions will be taken by the script")
        
for i in range(0,len(id)):

    log.output("  ---> Removing PATtuple with ID "+str(id[i])+" at "+storagePath[i])
    
for i in range(0,len(idTop)):
        
    log.output("  ---> Removing TopTree with ID "+str(idTop[i])+" at "+storagePathTop[i])

if not options.assume_yes:
    ans = str(raw_input('\n\nDo you want to continue? (y/n): '))
else:
    ans = "y"
    
if not ans == "n" and not ans == "y":
    
    print "\n\nWrong answer given!!!!\n\n"

    sys.exit(1)

elif ans == "n":

    print "\n\nNo actions where taken, killing this script\n\n"

    
else:

    log.output(" --> Starting the removal procedure")

    for i in range(0,len(id)):

        rmSRMdir(storagePath[i])

        rmFromTopDB("patuples",id[i])

        invalDBS(dbsPublish[i],CffFilePath[i])

    for i in range(0,len(idTop)):

        rmSRMdir(storagePathTop[i])

        rmFromTopDB("toptrees",idTop[i])

        rmTopTree(mergedTopLocation[i])


    if not options.rmDataSet == "None":

        rmFromTopDB("datasets",datasetID)
    
    
print ""
