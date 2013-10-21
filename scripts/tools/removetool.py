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

import shutil

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

        tmp = os.listdir(dir)

        n = 0
        
        for i in tmp:

            n=n+1
                        
            log.output("   ----> Removing file "+i)

            # do the removal

            cmd ='srmrm '+srmHost+dir+'/'+str(i)+' & '        
            pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            out = pExe.stdout.read()

            #print cmd

            if n == 10:
                cmd2="wait $!; echo done"
                #print cmd2
                pExe = Popen(cmd2, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                out = pExe.stdout.read()
                print out
                n=0
            
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

optParser.add_option("","--clean-up", action="store_true", dest="cleanup",default=bool(False),
                     help="This flag makes the script cross-reference all folders on PNFS with the TopDB database. Unmatched files will be removed from PNFS", metavar="")

optParser.add_option("","--assume-yes", action="store_true", dest="assume_yes",default=bool(False),
                     help="Answer yes to all questions", metavar="")

optParser.add_option("","--demo", action="store_true", dest="demo",default=bool(False),
                     help="If invoked, the remove commands will be put in a list to be mailed to the admins rather than executing them", metavar="")

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



#rmSRMdir("/pnfs/iihe/cms/store/user/dhondt/QCD_Pt-20to30_EMEnriched_TuneZ2_7TeV-pythia6/Spring11-PU_S1_START311_V1G1-v1/29032011_213110/TOPTREE")

#sys.exit(1)

#### Remove DataSet -> ALL associated PatTuples -> All associated TopTrees

if not options.cleanup and not options.rmDataSet == "None":

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

if not options.cleanup and not options.rmTopTree == "None":

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

if not options.cleanup and not options.rmPatonly == "None":

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

cleanup_dirsToRemove = []
cleanup_ldirsToRemove = []
if not options.cleanup and not options.rmPat == "None":

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

                        
## general clean-up

if options.cleanup:

    log.output("--> Cleaning up PNFS area/TopDB/Account for dhondt")

    log.output(" ---> Listing TopTrees that don't have a PNFS directory")

    sql.createQuery("SELECT","toptrees","id,StoragePath","")

    result2 = sql.execQuery().split('\n')

    for i in result2:

        if i == "" or not i.rfind("Storage") == -1: continue
    
        tid = i.split("\t")[0]

        dir = (i.split("\t")[1]).split("\n")[0]

        if not os.path.exists(dir+"/"):

            #print "-> TopTree ID "+id+" ("+dir+") not on PNFS"
            idTop.append(tid)
            storagePathTop.append(dir)
            mergedTopLocation.append(dir)

    log.output(" ---> Listing PATuples that don't have a TopTree assigned")

    sql.createQuery("SELECT","patuples","id,StoragePath,name,CffFilePath","")

    result2 = sql.execQuery().split('\n')

    sql.createQuery("SELECT","toptrees","patuple_id","")

    result3 = sql.execQuery().split('\n')

    for i in result2:

        continue # for now to protect samples for M. Segala

        if i == "" or not i.rfind("id") == -1:  continue

        tmpid = i.split("\t")[0]
        
        found=bool(False)

        for j in result3:

            if j == "": continue

            if tmpid == j:

                found=bool(True)

        if not found:

            #log.output("Patuple ID "+str(tmpid)+" has no TopTree assigned")

            id.append(i.split("\t")[0])
            storagePath.append(i.split("\t")[1])
            dbsPublish.append(i.split("\t")[2])
            CffFilePath.append(i.split("\t")[3])


    days=50

    log.output(" ---> Listing Configuration directories")
    log.output("   ---> Checking every Configuration directory (older than "+str(days)+" days) for large amounts of *.stdout from CRAB")

    ldirs = []

    basedir=(Popen("echo $HOME", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()).strip()+"/AutoMaticTopTreeProducer/"
    
    for dir in os.listdir(basedir):

        #continue

        if dir.rfind("CMSSW_") == -1:
            continue;

        pExe = Popen("find "+basedir+dir.strip()+"/ -name crab_*.cfg", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    
        out = pExe.stdout.read()

        #print out
        
        for file in out.split("\n"):
        
            split = file.split("/")
   
            dirName = ""
            for i in xrange(0,len(split)-1):
                dirName += split[i]+"/"

            dirName = dirName.rstrip("/")

            if ldirs.count(dirName) == 0 and len(dirName) > 0:
                ldirs.append(dirName.split("/AutoMaticTopTreeProducer/")[1]) # becase we don't want it to crash on changes /home /user

            # time to clean out some big chunks of stdout files
            if not dirName == "":

                filestat = os.stat(dirName)
            
                filedate = filestat.st_mtime
            
                now = int(time.time())
                
                last_mod=int(filedate)
                
                time_diff=now-last_mod
                
                if time_diff/(60*60*24) > days:

                    #log.output("    ---> Cleaning CRAB stdout files in "+dirName+" (Age: "+str(time_diff/(3600*24))+" days)")

                    crabdir=""

                    for dir in os.listdir(dirName):

                        if not dir.rfind("TOPTREE_") == -1 and dir.rfind(".py") == -1 and os.path.isdir(dirName+"/"+dir):
                            
                            crabdir=dirName+"/"+dir

                    if not crabdir == "":

                        numfiles=int(0)
                        
                        keepstdout=""
                        keepstderr=""
                        keepxml=""
                        for file in os.listdir(crabdir+"/res"):

                            if not file.rfind(".stdout") == -1:
                                if os.path.getsize(crabdir+"/res/"+file) > 0 and keepstdout == "": 
                                    keepstdout=file
                                numfiles=numfiles+1

                        #print numfiles

                        if not os.path.isdir(crabdir+"/res"):
                            numfiles=0
                            
                        if numfiles > 2 and dirName.rfind("Run201") == -1:

                            log.output("    ---> Cleaning CRAB stdout files in "+crabdir+" (Age: "+str(time_diff/(3600*24))+" days)")
                            #time.sleep(5)
                            #print keepstdout
                            keepstderr=keepstdout.split(".stdout")[0]+".stderr"
                            #print keepstderr
                            keepxml="crab_fjr_"+(keepstdout.split(".stdout")[0]).split("CMSSW_")[1]+".xml"
                            #print keepxml

                            for file in os.listdir(crabdir+"/res"):
                                
                                if not os.path.isdir(crabdir+"/res/"+file) and file.rfind("Submission") == -1 and file.rfind(".json") == -1 and not file == keepxml and not file == keepstdout and not file == keepstderr:
                                    log.output("      ---> Removing crab output "+file)
                                    os.unlink(crabdir+"/res/"+file)
                                elif not file.rfind("Submission") == -1:

                                    log.output("      ---> Removing old Submission_X dir: "+file)
                                    shutil.rmtree(crabdir+"/res/"+file)
                                    #sys.exit(1)

                        elif not dirName.rfind("Run201") == -1:

                            if os.path.exists(crabdir+"/res/.shrunk"):
                                continue

                            log.output("    ---> (DATA PRODUCTION) Removing unuseful lines from stdout files in "+crabdir+" (Age: "+str(time_diff/(3600*24))+" days)")
                            #time.sleep(5)

                            for file in os.listdir(crabdir+"/res"):
                                
                                if not file.rfind("Submission") == -1:
                                
                                    log.output("      ---> Removing old Submission_X dir: "+file)
                                    shutil.rmtree(crabdir+"/res/"+file)
                                    #sys.exit(1)

                                elif not os.path.isdir(crabdir+"/res/"+file) and file.rfind("Submission") == -1 and file.rfind(".json") == -1 and not file.rfind(".stdout") == -1:

                                    log.output("      ---> Shrinking crab output "+file)
                                    
                                    tmpfile = open(crabdir+"/res/"+file+"_tmp","w")

                                    for line in open(crabdir+"/res/"+file):
                                        if line.rfind("Begin processing") == -1 and line.rfind("Vertex") == -1 and line.rfind("%MSG") == -1:
                                            tmpfile.write(line)

                                    os.unlink(crabdir+"/res/"+file)
                                    os.rename(crabdir+"/res/"+file+"_tmp",crabdir+"/res/"+file)

                            f = open(crabdir+"/res/.shrunk","w") # leave a stamp that this dir is fixed
                            f.close()
                                    
                            #sys.exit(1)
       
            #log.output("  ----> "+str(len(dirs))+" directory(s) found up to now")

    log.output("  ----> "+str(len(ldirs))+" Configuration directory(s) found in total, cross-referencing TopDB...")

    #print ldirs

    #sys.exit(1)
    for i in xrange(0,len(ldirs)):

        #print ldirs[i]

        sql.createQuery("SELECT","toptrees","id","CffFilePath REGEXP '"+ldirs[i]+"'")

        result = sql.execQuery().split('\n')

        sql.createQuery("SELECT","patuples","id","CffFilePath REGEXP '"+ldirs[i]+"'")

        result2 = sql.execQuery().split('\n')

        sql.createQuery("SELECT","gensims","id","CffPath REGEXP '"+ldirs[i]+"'")

        result3 = sql.execQuery().split('\n')

        sql.createQuery("SELECT","recos","id","CffPath REGEXP '"+ldirs[i]+"'")

        result4 = sql.execQuery().split('\n')

        #print result
        #print result2

        if len(result) < 2 and len(result2) < 2 and len(result3) < 2 and len(result4) < 2 and cleanup_ldirsToRemove.count(ldirs[i]) == 0:

            filestat = os.stat(basedir+"/"+ldirs[i])
            
            filedate = filestat.st_mtime
            
            now = int(time.time())

            last_mod=int(filedate)

            time_diff=now-last_mod

            if time_diff/(60*60) > 480: # just want the dir to be old enough to not remove ongoing prod
            #if time_diff/(60*60) < 48: # just want the dir to be old enough to not remove ongoing prod

                #log.output("  ----> Directory "+ldirs[i]+" is not in TopDB, it should be removed!")
             
                #log.output("   ----> Age: "+time.ctime(now)+" - "+time.ctime(last_mod)+" = "+str(time_diff/(60*60))+"h")
            
                #sys.exit(1)
                
                cleanup_ldirsToRemove.append(ldirs[i])

    log.output("  ----> "+str(len(cleanup_ldirsToRemove))+" directory(s) need removal!")

    #sys.exit(1)

    log.output(" ---> Listing PNFS directories")

    dirs = []

    tmp=[]
    #tmp.append("WJetsToLNu_Tune*")
    #tmp.append("TTJ*")
    tmp.append("Mu*")
    for dir in os.listdir("/pnfs/iihe/cms/store/user/dhondt/"):
        
        if not dir.rfind("Skimmed-TopTrees") == -1:
            continue;

        #if dir.rfind("7TeV_T2") == -1: continue # this is just to make testing go fast
        
    #for dir in tmp:
        pExe = Popen("find /pnfs/iihe/cms/store/user/dhondt/"+dir+" -name *.root", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    
        out = pExe.stdout.read()

        #print out
        
        for file in out.split("\n"):
        
            split = file.split("/")
   
            dirName = ""
            for i in xrange(0,len(split)-1):
                dirName += split[i]+"/"

            dirName = dirName.rstrip("/")

            if dirs.count(dirName) == 0 and len(dirName) > 0:
                dirs.append(dirName)

            #log.output("  ----> "+str(len(dirs))+" directory(s) found up to now")

    log.output("  ----> "+str(len(dirs))+" directory(s) found in total, cross-referencing TopDB...")

    #for i in xrange(0,40):
    for i in xrange(0,len(dirs)):

        #print dirs[i]

        sql.createQuery("SELECT","toptrees","id","StoragePath REGEXP '"+dirs[i]+"'")

        result = sql.execQuery().split('\n')

        sql.createQuery("SELECT","patuples","id","StoragePath REGEXP '"+dirs[i]+"'")

        result2 = sql.execQuery().split('\n')

        sql.createQuery("SELECT","gensims","id","PNFSPath REGEXP '"+dirs[i]+"'")

        result3 = sql.execQuery().split('\n')

        sql.createQuery("SELECT","recos","id","PNFSPath REGEXP '"+dirs[i]+"'")

        result4 = sql.execQuery().split('\n')

        #print result
        #print result2

        #print result3
        #print result4
        
        if len(result) < 2 and len(result2) < 2 and len(result3) < 2 and len(result4) < 2 and cleanup_dirsToRemove.count(dirs[i]) == 0:

            filestat = os.stat(dirs[i])
            
            filedate = filestat.st_mtime
            
            now = int(time.time())

            last_mod=int(filedate)

            time_diff=now-last_mod

            if time_diff/(60*60) > 480: # just want the dir to be old enough to not remove ongoing prod
            #if time_diff/(60*60) > -100: # just want the dir to be old enough to not remove ongoing prod

                #log.output("  ----> Directory "+dirs[i]+" is not in TopDB, it should be removed!")

                #log.output("   ----> Age: "+time.ctime(now)+" - "+time.ctime(last_mod)+" = "+str(time_diff/(60*60))+"h")

                cleanup_dirsToRemove.append(dirs[i])

    log.output("  ----> "+str(len(cleanup_dirsToRemove))+" directory(s) need removal!")
    
    #sys.exit(0)

## general removal loop

if not options.cleanup and len(id) == 0 and len(idTop) == 0 and options.rmDataSet == "None":

    sys.exit()

if options.cleanup and len(cleanup_dirsToRemove) == 0 and len(cleanup_ldirsToRemove) == 0 and len(idTop) == 0 and len(id) == 0:

    sys.exit()

log.output(" --> The following actions will be taken by the script")

if not options.cleanup:
    for i in range(0,len(id)):
        
        log.output("  ---> Removing PATtuple with ID "+str(id[i])+" at "+storagePath[i])
        
        for i in range(0,len(idTop)):
            
            log.output("  ---> Removing TopTree with ID "+str(idTop[i])+" at "+storagePath[i])

else:
    
    time.sleep(5)
    for dir in cleanup_ldirsToRemove:
        filestat = os.stat(basedir+dir)
        filedate = filestat.st_mtime
        now = int(time.time())
        last_mod=int(filedate)
        time_diff=(now-last_mod)/(60*60*24)
        log.output("  ----> Removing Configuration dir "+dir+" which is not linked to a TopTree (Age: "+str(time_diff)+" days)")

    for dir in cleanup_dirsToRemove:
        filestat = os.stat(dir)
        filedate = filestat.st_mtime
        now = int(time.time())
        last_mod=int(filedate)
        time_diff=(now-last_mod)/(60*60*24)
        log.output("  ----> Removing "+dir+" which is not in TopDB (Age: "+str(time_diff)+" days)")

    for i in range(0,len(idTop)):
            
        log.output("  ---> Removing TopTree with ID "+str(idTop[i])+" at "+storagePathTop[i]+" which is not on PNFS anymore")

    for i in range(0,len(id)):
            
        log.output("  ---> Removing PATuple with ID "+str(id[i])+" which has no attached TopTrees")
     
        
if not options.assume_yes and not options.demo:
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
    #print id
    for i in range(0,len(id)):

        rmSRMdir(storagePath[i])

        rmFromTopDB("patuples",id[i])

        invalDBS(dbsPublish[i],CffFilePath[i])

    for i in range(0,len(idTop)):

        rmSRMdir(storagePathTop[i])

        rmFromTopDB("toptrees",idTop[i])

        rmTopTree(mergedTopLocation[i])

    for i in cleanup_ldirsToRemove:

        cmd = "cd "+basedir+"; rm -rfv "+i
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

        print pExe.stdout.read()

        log.output("  ---> Removed directory "+i)

    if options.demo:
         print ""
         print "Please mail the following to the grid admins"
         print ""

    for i in cleanup_dirsToRemove:

        if options.demo:
            print "rm -rfv "+str(i)    
        else:
            rmSRMdir(i)

    if not options.rmDataSet == "None":

        rmFromTopDB("datasets",datasetID)

    
print ""
