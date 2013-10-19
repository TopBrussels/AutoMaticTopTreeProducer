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
from time import strftime, gmtime, localtime
from datetime import datetime

# working with numbers
from math import sqrt

# import system to terminate process
import sys

# import pathname module
import os,os.path

# import logHandler
from logHandler import logHandler

# import mailHandler
from MailHandler import MailHandler

# import interface to topDB
from sqlHandler import SQLHandler

# import packages for multi-threading

import Queue
import threading

import shutil

####################
## Helper Classes ##
####################

class RemoveHelper:

    sql = ""
    log = ""

    def __init__(self,s,l):

        self.sql = s
        self.log = l
        
    def rmSRMdir (self,dir):

        srmHost = "srm://maite.iihe.ac.be:8443/"

        if os.path.exists(dir):

            self.log.output("  ---> Going into directory "+dir)

            tmp = os.listdir(dir)

            n = 0
        
            for i in tmp:

                n=n+1
                        
                self.log.output("   ----> Removing file "+i)

                # do the removal

                cmd ='srmrm '+srmHost+dir+'/'+str(i)+' & '        
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                out = pExe.stdout.read()
                            
                if n == 10:
                    cmd2="wait $!"
                    pExe = Popen(cmd2, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    out = pExe.stdout.read()
                    print out
                    n=0
            
            # do the removal
        
            splittedDir = dir.split("/")

            max = len(splittedDir)

            for i in range(0,5):

                if max > 7: # do not go under /pnfs/iihe/cms/store/user/USERNAME

                    toRemove = "/"
                    
                    for j in range(1,max):

                        toRemove += splittedDir[j]+"/"

                    #check if it's empty
                
                    if not os.listdir(toRemove):

                        self.log.output("   ----> Removing empty directory "+toRemove)

                        cmd ='srmrmdir '+srmHost+toRemove
            
                        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                        out = pExe.stdout.read()

                        #print cmd

                        self.log.output(out)

                max -= 1

    def rmFromTopDB(self,table,id):

        self.log.output("  ---> Removing entry "+str(id)+" from TopDB table "+table)

        self.sql.createQuery("DELETE",table,"*","id = '"+id+"'")

        self.sql.execQuery()

    def invalDBS(self,publishname,cmsDir):
    
        new= cmsDir.split("\\n")

        cmsDir = ""
    
        for i in range(0,len(new)):

            cmsDir += new[i]

            new= cmsDir.split("/")
                
            cmsDir = ""
    
        for i in range(0,len(new)-1):

            cmsDir += new[i]+'/'

        publishname = publishname.split("\\n")[0]

        self.log.output("  ---> Invalidating sample "+publishname+" in local DBS")

        initEnv = 'cd '+cmsDir+'; eval `scramv1 runtime -sh`; source /user/cmssoft/crab/latest/crab.sh'
    
        cmd = initEnv+'; DBSInvalidateDataset.py --DBSURL=https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet --datasetPath='+publishname
            
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()
    
        self.log.output(out)

class Request:

    ID=int(0)

    removeId=int(0)
    removeType=""
    user=""
    comment=""

    log=logHandler("")
    
    def __init__(self):

        # get the sensitive information from config file

        login=""
        password=""
        dbaseName=""
        dbaseHost=""

        for line in open(".config","r"):
            if not line.rfind("DBUser") == -1:
                login = line.split(" ")[1].split("\n")[0]
            elif not line.rfind("DBPass") == -1:
                password = line.split(" ")[1].split("\n")[0]
            elif not line.rfind("DBHost") == -1:
                dbaseHost = line.split(" ")[1].split("\n")[0]
            elif not line.rfind("DBName") == -1:
                dbaseName = line.split(" ")[1].split("\n")[0]

        self.sql = SQLHandler(dbaseName,login,password,dbaseHost)

    def setQueued(self):

        self.sql.createQuery("UPDATE","removals","","SET `Status` = 'Queued' WHERE `id` = "+str(self.ID)+" LIMIT 1")
        
        self.sql.execQuery()
        
    def setRunning(self):

        self.comment = self.comment+" <br>"+strftime("%Y-%m-%d %H:%M:%S", localtime())+": Starting removal"

        self.sql.createQuery("UPDATE","removals","","SET `Status` = 'Running' , `AdminAction` = '"+self.comment+"' WHERE `id` = "+str(self.ID)+" LIMIT 1")
        
        self.sql.execQuery()

    def setDone(self):

        self.comment = self.comment+" <br>"+strftime("%Y-%m-%d %H:%M:%S", localtime())+": Finished removal"

        self.sql.createQuery("UPDATE","removals","","SET `Status` = 'Done' , `AdminAction` = '"+self.comment+"' WHERE `id` = "+str(self.ID)+" LIMIT 1")
       
        self.sql.execQuery()

    def invalidate(self):

        self.comment = self.comment+" <br>"+strftime("%Y-%m-%d %H:%M:%S", localtime())+": <b>Error encountered during removal</b>"

        self.sql.createQuery("UPDATE","removals","","SET `Status` = 'Frozen', `AdminAction` = '"+self.comment+"'  WHERE `id` = "+str(self.ID)+" LIMIT 1")

        self.sql.execQuery()

    def process(self):

        # setup proper log location
        self.log = logHandler("logs/log-TopDB-CleaningAgent-"+str(self.ID)+".txt")

        self.log.output("****** Removing "+self.removeType+" with ID "+str(self.removeId)+" as requested by "+self.user+" ******")

        # pat to remove
        
        id = []
        storagePath = []
        dbsPublish = []
        CffFilePath = []
        
        # toptree to remove
        
        idTop = []
        storagePathTop = []
        mergedTopLocation = []

        storagePathTopMail=[]

        ## REMOVE ONLY TOPTREE
        if self.removeType == "toptree":
            
            self.sql.createQuery("SELECT","toptrees","id,StoragePath,TopTreeLocation","id = '"+str(self.removeId)+"'")
            
            result = self.sql.execQuery().split('\n')
            
            if len(result) == 1:
                
                self.log.output(" ---> ERROR: TopTree was not found in TopDB")
                
                return 1
            
            else:

                idTop.append(result[1].split("\t")[0])
                storagePathTop.append(result[1].split("\t")[1])
                mergedTopLocation.append(result[1].split("\t")[2])

        ## REMOVE PAT + ALL DOWNSTREAM TOPTREES

        elif self.removeType == "patuple":
            
            self.sql.createQuery("SELECT","patuples","id,StoragePath,name,CffFilePath","id = '"+str(self.removeId)+"'")
            result = self.sql.execQuery().split('\n')
            
            if len(result) == 1:

                self.log.output(" ---> RRROR: PatTuple was not found in TopDB")

                return 1
            
            else:

                id.append(result[1].split("\t")[0])
                storagePath.append(result[1].split("\t")[1])
                dbsPublish.append(result[1].split("\t")[2])
                CffFilePath.append(result[1].split("\t")[3])
                
                self.sql.createQuery("SELECT","toptrees","id,StoragePath,TopTreeLocation","patuple_id = '"+id[len(id)-1].split("\\n")[0]+"'")
                
                result2 = self.sql.execQuery().split('\n')
                
                if len(result2) > 1:

                    for j in range(1,len(result2)-1):

                        idTop.append(result2[j].split("\t")[0])
                        storagePathTop.append(result2[j].split("\t")[1])
                        mergedTopLocation.append(result2[j].split("\t")[2])
                        
        ## REMOVE DATASET + ALL DOWNSTREAM PAT + ALL DOWNSTREAM TOPTREES

        elif self.removeType == "dataset":    
                        
            self.sql.createQuery("SELECT","patuples","id,StoragePath,name,CffFilePath","dataset_id = '"+str(self.removeId)+"'")
            
            result = self.sql.execQuery().split('\n')

            if len(result) > 1:

                for i in range(1,len(result)-1):

                    id.append(result[i].split("\t")[0])
                    storagePath.append(result[i].split("\t")[1])
                    dbsPublish.append(result[i].split("\t")[2])
                    CffFilePath.append(result[i].split("\t")[3])
                    
                    self.sql.createQuery("SELECT","toptrees","id,StoragePath,TopTreeLocation","patuple_id = '"+id[len(id)-1].split("\\n")[0]+"'")
                    
                    result2 = self.sql.execQuery().split('\n')
                    
                    if len(result2) > 1:
                        
                        for j in range(1,len(result2)-1):
                            
                            idTop.append(result2[j].split("\t")[0])
                            storagePathTop.append(result2[j].split("\t")[1])
                            mergedTopLocation.append(result2[j].split("\t")[2])
                        
        ## CLEAN LEFTOVER FILES FROM FAILED PRODUCTION, CLEAN PATUPLES WITHOUT ANY TOPTREES
        elif self.removeType == "cleanpnfs":

            self.log.output("--> Cleaning up PNFS area for dhondt")

            self.log.output(" ---> Searching for PNFS directories from broken production")

            dirs = []

            for dir in os.listdir("/pnfs/iihe/cms/store/user/dhondt/"):
        
                if not dir.rfind("Skimmed-TopTrees") == -1:
                    continue;

                #if dir.rfind("7TeV_T2") == -1: continue # this is just to make testing go fast
        
                pExe = Popen("find /pnfs/iihe/cms/store/user/dhondt/"+dir+" -name TOPTREE", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    
                out = pExe.stdout.read()
        
                for file in out.split("\n"):
        
                    split = file.split("/")
   
                    dirName = ""
                    for i in xrange(0,len(split)-1):
                        dirName += split[i]+"/"

                    dirName = dirName.rstrip("/")

                    if dirs.count(dirName) == 0 and len(dirName) > 0:
                        dirs.append(dirName+"/TOPTREE")


            self.log.output("  ----> "+str(len(dirs))+" directory(s) found in total, cross-referencing TopDB...")

            for i in xrange(0,len(dirs)):

                self.sql.createQuery("SELECT","toptrees","id","StoragePath REGEXP '"+dirs[i]+"'")

                result = self.sql.execQuery().split('\n')
                
                self.sql.createQuery("SELECT","patuples","id","StoragePath REGEXP '"+dirs[i]+"'")
                
                result2 = self.sql.execQuery().split('\n')
                
                self.sql.createQuery("SELECT","gensims","id","PNFSPath REGEXP '"+dirs[i]+"'")
                
                result3 = self.sql.execQuery().split('\n')
                
                self.sql.createQuery("SELECT","recos","id","PNFSPath REGEXP '"+dirs[i]+"'")
                
                result4 = self.sql.execQuery().split('\n')
        
                if len(result) < 2 and len(result2) < 2 and len(result3) < 2 and len(result4) < 2 and storagePathTopMail.count(dirs[i]) == 0:

                    filestat = os.stat(dirs[i])
                    
                    filedate = filestat.st_mtime
                    
                    now = int(time.time())
                    
                    last_mod=int(filedate)
                    
                    time_diff=now-last_mod
                    
                    if time_diff/(60*60) > 720: # just want the dir to be old enough to not remove ongoing prod

                        self.log.output("  ----> Directory "+dirs[i]+" is not in TopDB, it should be removed! (Age: "+str(time_diff/(60*60*24))+" days)")

                        #idTop.append(-9999)
                        storagePathTopMail.append(dirs[i])

            self.log.output("  ----> "+str(len(storagePathTopMail))+" directory(s) need removal!")
    
            self.log.output(" ---> Searching for PATuples that don't have a TopTree assigned")

            self.sql.createQuery("SELECT","patuples","id,StoragePath,name,CffFilePath","")

            result2 = self.sql.execQuery().split('\n')
            
            self.sql.createQuery("SELECT","toptrees","patuple_id","")

            result3 = self.sql.execQuery().split('\n')

            for i in result2:

                if i == "" or not i.rfind("id") == -1:  continue

                tmpid = i.split("\t")[0]
        
                found=bool(False)

                for j in result3:

                    if j == "": continue

                    if tmpid == j:

                        found=bool(True)

                #if not found:

                    #id.append(i.split("\t")[0])
                    #storagePath.append(i.split("\t")[1])
                    #dbsPublish.append(i.split("\t")[2])
                    #CffFilePath.append(i.split("\t")[3])

            msg = "Dear admins,"

            if len(storagePathTopMail) > 0:
                msg += "\n\n The automatic TopDB PNFS cleaning tool has found "+str(len(storagePathTopMail))+" directories on PNFS not corresponding to any entry in the TopDB database."

                msg += "\n\n Please have a look at the following list:"

                for s in storagePathTopMail:

                    msg += "\n\n \t rm -rfv "+s

            else:
                msg += "\n\n The automatic TopDB PNFS cleaning tool has found NO directories on PNFS not corresponding to any entry in the TopDB database."

            msg += "\n\nCheers,\nHector the cleaning agent"

            mail = MailHandler()

            mail.sendMail("error","Report from TopDB PNFS cleaning",msg)


        ## CLEAN LEFTOVER FILES FROM FAILED PRODUCTION, CLEAN PATUPLES WITHOUT ANY TOPTREES
        elif self.removeType == "cleancrablogs":

            days=50

            self.log.output(" ---> Listing Configuration directories")
            self.log.output("   ---> Checking every Configuration directory (older than "+str(days)+" days) for large amounts of *.stdout from CRAB")

            ldirs = []
            cleanup_ldirsToRemove = []
            
            basedir=(Popen("echo $HOME", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()).strip()+"/AutoMaticTopTreeProducer/"
    
            for dir in os.listdir(basedir):

                if dir.rfind("CMSSW_") == -1:
                    continue;

                pExe = Popen("find "+basedir+dir.strip()+"/ -name crab_*.cfg", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    
                out = pExe.stdout.read()
        
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

                        if not dirName.find("find: ") == -1:
                            dirName = dirName.split("find: ")[1]
                        #print dirName

                        filestat = os.stat(dirName)
                    
                        filedate = filestat.st_mtime
                        
                        now = int(time.time())
                        
                        last_mod=int(filedate)
                        
                        time_diff=now-last_mod
                        
                        if time_diff/(60*60*24) > days:
                            
                            #self.log.output("    ---> Cleaning CRAB stdout files in "+dirName+" (Age: "+str(time_diff/(3600*24))+" days)")
                            
                            crabdir=""

                            for dir in os.listdir(dirName):

                                if not dir.rfind("TOPTREE_") == -1 and dir.rfind(".py") == -1 and os.path.isdir(dirName+"/"+dir):
                                
                                    crabdir=dirName+"/"+dir

                            if not crabdir == "":

                                numfiles=int(0)
                        
                                keepstdout=""
                                keepstderr=""
                                keepxml=""

                                if os.path.exists(crabdir+"/log/crab.log"):

                                    self.log.output("    ---> Cleaning crab.log in "+crabdir+"/log/ (Age: "+str(time_diff/(3600*24))+" days)")

                                    os.unlink(crabdir+"/log/crab.log")

                                    #sys.exit(1)
                                    
                                for file in os.listdir(crabdir+"/res"):

                                    if not file.rfind(".stdout") == -1:
                                        if os.path.getsize(crabdir+"/res/"+file) > 0 and keepstdout == "": 
                                            keepstdout=file
                                        numfiles=numfiles+1

                                #print keepstdout

                                if not os.path.isdir(crabdir+"/res"):
                                    numfiles=0

                                #print numfiles

                                #print str(numfiles)+" "+dirName
                            
                                if numfiles > 2 and dirName.rfind("Run201") == -1:

                                    print numfiles

                                    self.log.output("    ---> Cleaning CRAB stdout files in "+crabdir+" (Age: "+str(time_diff/(3600*24))+" days)")
                            
                                    keepstderr=keepstdout.split(".stdout")[0]+".stderr"

                                    keepxml="crab_fjr_"+(keepstdout.split(".stdout")[0]).split("CMSSW_")[1]+".xml"
                                    
                                    for file in os.listdir(crabdir+"/res"):
                                
                                        if not os.path.isdir(crabdir+"/res/"+file) and file.rfind("Submission") == -1 and file.rfind(".json") == -1 and not file == keepxml and not file == keepstdout and not file == keepstderr:
                                            self.log.output("      ---> Removing crab output "+file)
                                            os.unlink(crabdir+"/res/"+file)
                                        elif not file.rfind("Submission") == -1:

                                            self.log.output("      ---> Removing old Submission_X dir: "+file)
                                            shutil.rmtree(crabdir+"/res/"+file)

                                elif not dirName.rfind("Run201") == -1:

                                    if os.path.exists(crabdir+"/res/.shrunk"):
                                        continue

                                    self.log.output("    ---> (DATA PRODUCTION) Removing unuseful lines from stdout files in "+crabdir+" (Age: "+str(time_diff/(3600*24))+" days)")

                                    for file in os.listdir(crabdir+"/res"):
                                
                                        if not file.rfind("Submission") == -1:
                                
                                            self.log.output("      ---> Removing old Submission_X dir: "+file)
                                            shutil.rmtree(crabdir+"/res/"+file)

                                        elif not os.path.isdir(crabdir+"/res/"+file) and file.rfind("Submission") == -1 and file.rfind(".json") == -1 and not file.rfind(".stdout") == -1:

                                            self.log.output("      ---> Shrinking crab output "+file)
                                    
                                            tmpfile = open(crabdir+"/res/"+file+"_tmp","w")
                                        
                                            for line in open(crabdir+"/res/"+file):
                                                if line.rfind("Begin processing") == -1 and line.rfind("Vertex") == -1 and line.rfind("%MSG") == -1:
                                                    tmpfile.write(line)

                                            os.unlink(crabdir+"/res/"+file)
                                            os.rename(crabdir+"/res/"+file+"_tmp",crabdir+"/res/"+file)

                                    f = open(crabdir+"/res/.shrunk","w") # leave a stamp that this dir is fixed
                                    f.close()
                                
            self.log.output("  ----> "+str(len(ldirs))+" Configuration directory(s) found in total, cross-referencing TopDB...")

            self.log.output("")

            ldirs = [] # disable this for now
            
            for i in xrange(0,len(ldirs)):

                self.sql.createQuery("SELECT","toptrees","id","CffFilePath REGEXP '"+ldirs[i]+"'")
                
                result = self.sql.execQuery().split('\n')
                
                self.sql.createQuery("SELECT","patuples","id","CffFilePath REGEXP '"+ldirs[i]+"'")
                
                result2 = self.sql.execQuery().split('\n')
                
                self.sql.createQuery("SELECT","gensims","id","CffPath REGEXP '"+ldirs[i]+"'")
                
                result3 = self.sql.execQuery().split('\n')
                
                self.sql.createQuery("SELECT","recos","id","CffPath REGEXP '"+ldirs[i]+"'")
                
                result4 = self.sql.execQuery().split('\n')
                
                if len(result) < 2 and len(result2) < 2 and len(result3) < 2 and len(result4) < 2 and cleanup_ldirsToRemove.count(ldirs[i]) == 0:
                    
                    filestat = os.stat(basedir+"/"+ldirs[i])
                    
                    filedate = filestat.st_mtime
                    
                    now = int(time.time())
                    
                    last_mod=int(filedate)
                    
                    time_diff=now-last_mod
                    
                    if time_diff/(60*60*24) > days: # just want the dir to be old enough to not remove ongoing prod
                        
                        self.log.output("  ----> Directory "+ldirs[i]+" is not in TopDB, it should be removed! (Age: "+str(time_diff/(60*60*24))+" days)")
                        
                        cleanup_ldirsToRemove.append(ldirs[i])
                        
            self.log.output("  ----> "+str(len(cleanup_ldirsToRemove))+" directory(s) need removal!")


        ## SUMMARY OF THE REMOVAL

        self.log.output(" --> Summary of the removal")
        
        for i in range(0,len(id)):
        
            self.log.output("  * Removing PATtuple with ID "+str(id[i])+" at "+storagePath[i])
        
        for i in range(0,len(idTop)):
                
            self.log.output("  * Removing TopTree with ID "+str(idTop[i])+" at "+storagePathTop[i])

        #if self.removeType == "cleanpnfs":
        #    return 0;
        
        # START REMOVAL

        time.sleep(20)

        log.output(" --> Starting the removal procedure")

        rm = RemoveHelper(self.sql,self.log)

        for i in range(0,len(id)):

            rm.rmSRMdir(storagePath[i])

            rm.rmFromTopDB("patuples",id[i])

            rm.invalDBS(dbsPublish[i],CffFilePath[i])

        for i in range(0,len(idTop)):

            rm.rmSRMdir(storagePathTop[i])

            if idTop[i] > 0:
                rm.rmFromTopDB("toptrees",idTop[i])

        if self.removeType == "dataset":

            rm.rmFromTopDB("datasets",self.removeId)

        self.log.output(" --> Ended removal procedure")
        return 0
    
    def resetQueue(self):

        self.sql.createQuery("UPDATE","removals","","SET `Status` = 'Pending' WHERE `Status` = 'Queued'")
            
        self.sql.execQuery()


class RequestHandler:

    sleepTime = int(30)

    requests = []
        
    def __init__(self):

        # get the sensitive information from config file

        login=""
        password=""
        dbaseName=""
        dbaseHost=""

        for line in open(".config","r"):
            if not line.rfind("DBUser") == -1:
                login = line.split(" ")[1].split("\n")[0]
            elif not line.rfind("DBPass") == -1:
                password = line.split(" ")[1].split("\n")[0]
            elif not line.rfind("DBHost") == -1:
                dbaseHost = line.split(" ")[1].split("\n")[0]
            elif not line.rfind("DBName") == -1:
                dbaseName = line.split(" ")[1].split("\n")[0]

        self.sql = SQLHandler(dbaseName,login,password,dbaseHost)

        self.getProperties()

  
    def getProperties(self):
        
        self.sql.createQuery("SELECT","removals","*","Status = 'Pending' OR Status = 'Queued' ORDER BY `ID` DESC")

        timestamp = strftime("%d%m%Y_%H%M%S")

        f = open("sql"+str(timestamp)+".out","w")
        f.write(self.sql.execQuery())
        f.close()

        for res in open("sql"+str(timestamp)+".out","r"):

            #print res
            
            line = res.split("\n")[0]
            sqlRes = line.split("	")

            for a in xrange(len(sqlRes)):
                sqlRes[a]=sqlRes[a].split("\n")[0]
                sqlRes[a]=sqlRes[a].split("\r")[0]
            
            if sqlRes[0].rfind("ID") == -1 and len(sqlRes) > 6:
                
                request = Request()
                
                request.ID = sqlRes[0]
                request.removeId = sqlRes[4]
                request.removeType = sqlRes[3]
                request.user = sqlRes[1]
                request.comment = sqlRes[6]
                
                self.requests.append(request)

        os.remove("sql"+str(timestamp)+".out")

################################
## WORKER CLASS FOR THREADING ##
################################
        
class WorkFlow (threading.Thread ):

    def __init__(self, *args, **kwds):

        threading.Thread.__init__(self, *args, **kwds)
    
        self.keepAlive = bool(True)

    def stop (self):
        
        self.keepAlive = bool(False)


    def run (self):
        
        # our thread runs forever
        
        while True:

            if not self.keepAlive:

                break

            # get the request from the queue

            request = requestsPool.get()

            log.output("--> Starting production for request "+request.ID)

            request.setRunning()

            exitCode = request.process() # running AutoMaticSIMProducer
                    
            if exitCode == 0:

                log.output("--> Production for request "+request.ID+" is finished, removing request from TopDB!")

                request.setDone()

            elif exitCode == 1:

                log.output(" ---> The script encountered a python error for request "+request.ID+", sending email to admins!")
                
                request.invalidate()
                
                # put all queued requests on hold again
                
                request.resetQueue()
                
                # send email
                
                sendErrorMail(exitCode,request.ID)
                
                #sys.exit(1)
                
            elif exitCode == 2:

                log.output(" ---> Something is wrong in the configuration for request "+request.ID+". Disabling this entry and sending a mail for manual intervention")
                
                request.invalidate()
                
                # send email
                
                sendErrorMail(exitCode,request.ID)

#############
## METHODS ##
#############


def sendErrorMail(exitCode,ID):

    global log
    global options

    cmd ='pwd'
    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    dir = pExe.stdout.read()
        
    log.output("********** SCRIPT GOT TERMINATE SIGNAL -> ALERTING PRODUCTION TEAM **********")
        
    mail = MailHandler()

    type = "error"

    subject = "Problem within the Simulation Workflow"

    msg = "Dear top quark group,\n"
    msg += "\n"
    msg += "This is an automatically generated e-mail to inform you that the production workflow encountered problems during the processing of request "+ID+"."
    msg += "\n\nReason:"
    if exitCode == 1:
        msg += "\n\n\t AutomaticSIMProducer exited with code 1 -> probabely a python exception. The workflow is now terminated. Please investigate and restart the workflow."
    if exitCode == 2:
        msg += "\n\n\t AutoMaticSIMProducer encountered a problem in the request configuration. This request is put inactive (Priority 0) until manual intervention."
    msg += "\n\nSTDOUT log: "+dir+"/"+"stdout"
    
    msg += "\n\n\nCheers,\nSIMProduction.py"

    #if not options.dryRun:
        #mail.sendMail(type,subject,msg)


def getnWorkers():

    for line in open(".config","r"):
        if not line.rfind("nWorkersCleaningAgent") == -1:
            return int(line.split(" ")[1].split("\n")[0])

    return int(0)

###################
## OPTION PARSER ##
###################

# Parse the options
optParser = OptionParser()

optParser.add_option("","--dry-run", action="store_true", dest="dryRun",default=bool(False),
                     help="Perform a Dry Run (e.g.: no real submission)", metavar="")

optParser.add_option("","--log-stdout", action="store_true", dest="stdout",default=bool(False),
                     help="Write output to stdout and not to logs/log-*.txt", metavar="")


(options, args) = optParser.parse_args()

#if options.cmssw_ver == None:
#    optParser.error("Please specify a CMSSW version.\n")

#################
## DEFINITIONS ##
#################

if not options.stdout == True:
    log = logHandler("logs/CleaningAgentWorkFlow.txt")
else:
    log = logHandler("")

#################
## MAIN METHOD ##
#################
    
# Create our Queue to store requests:

requestsPool = Queue.Queue ( 0 )

# check the # of workers to start

nWorkers=getnWorkers()

log.output("-- Starting the workflow with "+str(nWorkers)+" workers --")

# start our X threads

workers = []
for x in xrange ( nWorkers ):
   workers.append(WorkFlow())
   workers[x].start()

# setup the request and fill the queue

while True:

    # check if we need to start/kill threads

    nWorkers = len(workers)

    targetnWorkers = getnWorkers()

    if nWorkers < targetnWorkers:

        log.output("-- Number of requested workers changed to "+str(targetnWorkers)+" -> adding "+str(targetnWorkers-nWorkers)+" workers --")

        for x in xrange ( targetnWorkers-nWorkers ):
            workers.append(WorkFlow())
            workers[len(workers)-1].start()
            time.sleep(5) # to make shure not more than 1 process uses sql

    if nWorkers > targetnWorkers:

        log.output("-- Number of requested workers changed to "+str(targetnWorkers)+" -> removing "+str(-targetnWorkers+nWorkers)+" workers --")

        for x in xrange ( nWorkers-targetnWorkers ):
            workers.pop(len(workers)-1).stop()

    nWorkers = len(workers)

    log.output("-- Worker status -> "+str(nWorkers)+" running --")

    # with 0 workers, there is no need to do anything....

    if nWorkers == 0:

        time.sleep(3600)

        continue

    # check if there is a worker that died
    
    for worker in workers:

        #print worker

        if not worker.isAlive(): # if ANY of our workers died -> kill program

            log.output("--ERROR-- One of the workers died, exiting")
            #sys.exit(1)

    log.output("-> Polling TopDB");

    # empty the pool
    while not requestsPool.empty():

        requestsPool.get()
    
    req = RequestHandler()

    for i in req.requests:

        i.setQueued()

        #log.output(i.DataSet+" -> Priority: "+str(i.Priority))

        requestsPool.put(i)

        time.sleep(5) # to make shure not more than 1 process uses sql

    #while not requestsPool.empty():

    #    print requestsPool.get().DataSet

    del req.requests[:] # empty requests container
    
    time.sleep(1800)
