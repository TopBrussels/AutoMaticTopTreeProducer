#this class uses the dbs api to handle dbs queries

# working with time
import time
from time import strftime
from datetime import datetime

# regular expressions
import re

# interacting with the os
import subprocess
from subprocess import Popen, PIPE, STDOUT

import os, os.path

import sys

class DBSHandler:

    def __init__ (self,dbsInst):

        self.dbsInst = "http://cmsdbsprod.cern.ch/"+dbsInst+"/servlet/DBSServlet"

        #self.sourceDBSApi = "source /jefmount_mnt/jefmount/cmss/slc5_ia32_gcc434/cms/dbs-client/DBS_2_0_*/etc/profile.d/init.sh; "
        self.sourceDBSApi = "source /jefmount_mnt/jefmount/cmss/slc5_amd64_gcc434/cms/dbs-client/DBS_2_1_*/etc/profile.d/init.sh; "

    def setDBSInst(self,string):

        self.dbsInst = "http://cmsdbsprod.cern.ch/"+string+"/servlet/DBSServlet"

    def datasetExists(self,dataset):

        dataset = dataset.split('\n')[0];
        
        dbsCmd = self.sourceDBSApi+" dbs lsd --url="+self.dbsInst+" --path="+dataset+" | grep "+dataset

        pExe = Popen(dbsCmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()

        if not out.split('\n')[0].rfind(dataset) == -1:

            return bool(True)

        return bool(False)
        
    def getTotalEvents(self,dataset,runlist):

        dataset = dataset.split('\n')[0];

        if not type(runlist) == type([]):

            return -1

        if len(runlist) == 0:

            totalEvents = int(0)
        
            dbsCmd = self.sourceDBSApi+" dbs lsf --url="+self.dbsInst+" --path="+dataset+" --report | grep NumberOfEvents"

            pExe = Popen(dbsCmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            out = pExe.stdout.read()

            #print out

            for i in out.split("\n"):

                split = i.split("NumberOfEvents : ")

                if (len(split) == 2):

                    totalEvents += int(split[1])
                
            return totalEvents

        else:

            totalEvents = int(0)

            for run in runlist:

                #print "looking at run "+str(run)

                dbsCmd = self.sourceDBSApi+" dbs lsf --url="+self.dbsInst+" --path="+dataset+" --run="+str(run)+" --report | grep NumberOfEvents"
            
                pExe = Popen(dbsCmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                out = pExe.stdout.read()

                for i in out.split("\n"):

                    split = i.split("NumberOfEvents : ")
            
                    if (len(split) == 2):

                        totalEvents += int(split[1])
                        
            return totalEvents

        return 0


#dbs = DBSHandler("cms_dbs_prod_global")

#print dbs.getTotalEvents("/MinimumBias/Commissioning10-SD_Mu-v9/RECO",[])

#print dbs.getTotalEvents("/MinimumBias/Commissioning10-SD_Mu-v9/RECO",[133874,134800])

#print dbs.datasetExists("/MuHad/Run2012A-13Jul2012-v1/AOD")
#print dbs.getTotalEvents("/MuHad/Run2012A-13Jul2012-v1/AOD",[])

#dbs2 = DBSHandler("cms_dbs_ph_analysis_02")

#ds = '/SingleTop_sChannel-madgraph/dhondt-PAT_SingleTop_sChannel-madgraph_Spring10-START3X_V26_S09-v1_11062010_093308-09ac191e07064fca2fda7ee6494480b8/USER'

#print dbs2.datasetExists(ds) /MuHad/Run2012A-13Jul2012-v1/AOD 

#print dbs2.getTotalEvents(ds,[])

#print dbs2.getTotalEvents("/MinimumBias/dhondt-PAT_MinimumBias_Commissioning10-May6thPDSkim2_SD_Mu-v1_19052010_115800-c6f014c4a9c071b2e7bb89b828ec57a8/USER ",[])


