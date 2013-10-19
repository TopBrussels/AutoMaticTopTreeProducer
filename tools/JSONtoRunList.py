# python script to convert JSON to runlist

# regular expressions
import re

# interacting with the os
from subprocess import Popen, PIPE, STDOUT
import sys
import os, os.path

# working with time
import time
from time import strftime, gmtime
from datetime import datetime


# main

print ""

timestamp = strftime("%d%m%Y_%H%M%S")

if not sys.argv[1].rfind("http://") == 0 and not sys.argv[1].rfind("https://") == 0:

    print "Usage: python JSONtoRunList.py <JSON url>"

    sys.exit(0)

    
# get the JSON file

print "+> Getting runlist from "+sys.argv[1].split("/")[len(sys.argv[1].split("/"))-1]
cmd ='wget --no-check-certificate -O JSON_'+timestamp+'.txt '+sys.argv[1]+'; cat JSON_'+timestamp+'.txt'

#print cmd
pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
out = pExe.stdout.read()

# get the runs

print ""

runlist = []

for run in out.split(","):

    if not run.rfind("\"") == -1:

        runlist.append(run.split("\"")[1])

print " ++> Number of runs: "+str(len(runlist))

runstring = ""

for run in runlist:
    
    runstring += run

    if not run == runlist[len(runlist)-1]:

        runstring += ","
print ""
print " ++> RunList: "+runstring
        
# remove the json file

if os.path.exists('JSON_'+timestamp+'.txt'):
    os.remove('JSON_'+timestamp+'.txt')

print ""
