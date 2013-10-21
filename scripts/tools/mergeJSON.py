#
# getLumi.py - Copyright 2010 Mario Kadastik
#
# Version 1.0, date 12 April 2010
# 
# This is a temporary tool to calculate the integrated luminosity of CMS based on a JSON file
#
# Usage: python getLumi.py crabReport.json official.json
#

import json, sys

my_crab_json=file(sys.argv[1],'r')
my_crab_dict = json.load(my_crab_json)
official_lumi_json=file(sys.argv[2],'r')
official_lumi_dict = json.load(official_lumi_json)

# now get our json stuff

# compare our json with the official json

# store keywords for official json
kw_official_json = []
for k, v in official_lumi_dict.items():
  for lumis in v:
#    print "k:", k, " v:", v, " lumis:", lumis
    if type(lumis) == type([]) and len(lumis) == 2:
      for i in range(lumis[0], lumis[1] + 1):
        kw="%d_%d" % (int(k),int(i))
#        print kw
        kw_official_json.append(kw)

# cross-check them with ours and fill the final dict
kw_final_json = []
for k, v in my_crab_dict.items():
  for lumis in v:
    if type(lumis) == type([]) and len(lumis) == 2:
      for i in range(lumis[0], lumis[1] + 1):
        kw="%d_%d" % (int(k),int(i))
        if kw in kw_official_json:
          kw_final_json.append(kw)
#	  print kw

print "len(kw_official_json) =", len(kw_official_json)
print "len(kw_final_json)", len(kw_final_json)

final_json_string = "{"
previous_run = -1
previous_lumi = -1
for k in kw_final_json:
  splitted = k.split("_")
  run = splitted[0]
  lumi = splitted[1]
  if len(lumi) > 0:
    if run != previous_run:
      if previous_run != -1:
        final_json_string += str(previous_lumi) + "]], "
      final_json_string += "\"" + str(run) + "\": [["
      previous_run = run
      previous_lumi = -1
    if int(previous_lumi) != ( int(lumi) - 1 ):
      if previous_lumi != -1:
        final_json_string += str(previous_lumi) + "], ["
      final_json_string += str(lumi) + ", "
    previous_lumi = lumi
  else:
    print "Possible problem: len(lumi) =", len(lumi)
    print "k =", k

final_json_string += str(previous_lumi) + "]]}"

print "final JSON:"
print final_json_string
