# Class to Collect PNFS files on demand of mtop

# interacting with the os

from subprocess import Popen, PIPE, STDOUT

from datetime import datetime

import time

import sys

import os, os.path

import math

#############
## METHODS ##
#############

def writeFile(fileName,line):

    f = open(fileName,"a")

    f.write(line+"\n")

    f.close()

####################
## INITIALISATION ##
####################

srm = "srm://maite.iihe.ac.be:8443/"

workingDir = ""

#get homedir 
#cmd ='echo $HOME'
#pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
#homeDir = pExe.stdout.read().split('\n')[0]
homeDir="/user/TopSkim"

#making directory structure

dir = []

dir.append(homeDir+"/TopTrees")

dir.append(dir[len(dir)-1]+"/tmp/")

# start endless loop checking for a request

while True:

    if os.path.exists(homeDir+"/TopTrees/request.txt"):

	# create grid proxy

        # get certificate password from config
        password=""
        for line in open(".config","r"):
            if not line.rfind("GridPass") == -1:
                password = line.split(" ")[1]

        cmd ='voms-proxy-init -voms cms:/cms/becms -valid 190:00 -pwstdin'
        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    
        pExe.communicate(password)

        # getting request information

        request = open(homeDir+"/TopTrees/request.txt").readlines()

        if len(request) == 1:
            
            destination = request[0].split(":")[0].split('\n')[0]
            source = request[0].split(":")[1].split('\n')[0]

            dir.append(dir[len(dir)-1]+"/"+destination)

            print destination
            print source

            for i in range(0,len(dir)):
            
                if not os.path.exists(dir[i]):

                    print " ---> Creating directory: "+dir[i]

                    os.makedirs(dir[i])
                
                    workingDir = dir[len(dir)-1]
                    
                    # get source directory content

            cmd = 'ls '+source+' | grep -v BADFILE'
            pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            out = pExe.stdout.read()

            # open request.txt again and update it with the latest info
        
            files = out.split("\n")

            nFiles = len(files)-1

            #nFiles = int(2)

            #time.sleep(30) # for testing

            writeFile(homeDir+"/TopTrees/request.txt","nFiles: "+str(nFiles)) # store number of files in report

            #print out.split("\n")

            for i in xrange ( nFiles ):

                downloadcmd ='source /opt/external/etc/profile.d/grid-env.sh; nice lcg-cp '+srm+source+"/"+files[i]+" file:///"+workingDir+"/TopTree_"+str(i+1)+".root; chmod 777 "+workingDir+"/.. -R"
                print str(i)+" "+downloadcmd
                                
                d = Popen(downloadcmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                out = d.stdout.read()

                print out

                writeFile(homeDir+"/TopTrees/request.txt","File "+str(i+1)+": DONE")


            # remove the current tmp dir from the list

            dir.pop(len(dir)-1)

        else:

            print "Process still in progress, sleeping"

            time.sleep(60)

    else:

        print "No request present, sleeping"

    time.sleep(60)
