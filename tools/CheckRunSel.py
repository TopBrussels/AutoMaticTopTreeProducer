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

import math

from DBSHandler import DBSHandler


dbs = DBSHandler("cms_dbs_prod_global")

if not dbs.datasetExists(sys.argv[1]):

    print "ERROR: Dataset does not exist in DBS"
    sys.exit(0)
    
else:

    print "Total nEvents: "+str(dbs.getTotalEvents(sys.argv[1],[]))

for line in open(sys.argv[2],"r"):
        
    runs = line.strip().split(",")

    #print runs

    nEvPerJob = 20000

    nEvents = int(dbs.getTotalEvents(sys.argv[1],runs))


    if nEvents > 10000000:
        nEvPerJob = 20000

    elif nEvents > 5000000 and nEvents < 10000000:
        nEvPerJob = int(math.ceil(nEvents/(450)))
    
    print "\n* "+line+" -> nEv: "+str(nEvents)+" nJobs: "+str(nEvents/nEvPerJob)


