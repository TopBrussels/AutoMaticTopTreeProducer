#!/usr/bin/env python
# Author: Tae.Jeong.Kim@cern.ch
import os
import re
import sys
import time
import commands

from optparse import OptionParser


parser = OptionParser()
parser.add_option("-f", "--dataset-file", dest="filename",
                  help="dataset list", metavar="FILE")

parser.add_option("","--mc", action="store_true", dest="runOnMC",help="Specify it is MC")
parser.add_option("","--data", action="store_false", dest="runOnMC",help="Specify it is Data")

(options, args) = parser.parse_args()

filename = options.filename
datasets = open(filename,'r').read().split('\n')[:-1]

cmsswbase = commands.getoutput("echo $CMSSW_BASE")

for dataset in datasets:
  runOnMC = "--mc"
  if not options.runOnMC: 
    runOnMC = "--data"
  os.system("python "+cmsswbase+"/src/TopBrussels/AutoMaticTopTreeProducer/scripts/AutoMaticTopTreeProducer.py -v V5_0_1 -d "+dataset+" --dont-store-pat true "+runOnMC+" &")
