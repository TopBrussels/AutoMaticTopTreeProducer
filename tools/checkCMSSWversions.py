# python script to sync the installed CMSSW releases and the topDB cmsswversion table

# interacting with the os
from subprocess import Popen, PIPE, STDOUT
import sys
import os, os.path

# time
import time, datetime

# sql interface
from sqlHandler import SQLHandler

# get the sensitive information from config file

login=""
password=""
dbaseName=""
dbaseHost=""

baseDir = "/user/dhondt/AutoMaticTopTreeProducer"
        
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

# checking the CMSSW versions installed -> insert into topDB where needed

for entry in os.listdir(baseDir):

    if os.path.isdir(baseDir+"/"+entry) == True and not entry.rfind("CMSSW") == -1:

        print "Local version found: "+entry

        isInDB = bool(False)

        # check if this version exists in topDB otherwise add it
        
        options="version REGEXP '"+entry+"'"
        
        sql.createQuery("SELECT","cmsswversions","version",options)
        
        f = open("sql.out","w")
        f.write(sql.execQuery())
        f.close()
        
        for line in open("sql.out","r"):

            if not line.rfind(entry) == -1:

                print " --> Ok, this version is in the topDB"

                isInDB = True
        
        os.remove("sql.out")

        if not isInDB:

            print " --> Adding this version to topDB"

            initEnv = 'cd '+baseDir+'/'+entry+'; eval `scramv1 runtime -sh`;'

            cmd = initEnv+"showtags"
            pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            out = pExe.stdout.read().split("\n")

            tags = ""
            
            for tag in out:

                tags = tags+tag+"<br>"

            # add info to db

            values = []
            values.append([])
            values[len(values)-1].append("version")
            values[len(values)-1].append(entry)

            values.append([])
            values[len(values)-1].append("CMSSWtags")
            values[len(values)-1].append(tags)


            #print tags

            sql.createQuery("INSERT INTO","cmsswversions","",values)

            print sql.execQuery()



# checking CMSSW versions in topDB -> remove obsolete ones

sql.createQuery("SELECT","cmsswversions","version","")
        
f = open("sql.out","w")
f.write(sql.execQuery())
f.close()
        
for line in open("sql.out","r"):

    if not line.rfind("CMSSW") == -1:

        version = line.split("\n")[0]

        print "TopDB CMSSW version found: "+version

        isInstalled = bool(False)

        for entry in os.listdir(baseDir):

            if os.path.isdir(baseDir+"/"+entry) == True and not entry.rfind("CMSSW") == -1:
                
                if not version.rfind(entry) == -1:

                    print " --> Ok, this version is installed in the AutoMaticTopTreeProducer"

                    isInstalled = True

        if not isInstalled:

            print " --> This version is not installed, removing from TopDB"

            # remove info from db

            values = "version = '"+version+"'"


            #print tags

            sql.createQuery("DELETE","cmsswversions","",values)

            sql.execQuery()
                    
os.remove("sql.out")
