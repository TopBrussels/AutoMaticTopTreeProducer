#
# getLumi.py - Copyright 2010 Mario Kadastik
#
# Version 1.0, date 12 April 2010
# 
# This is a temporary tool to calculate the integrated luminosity of CMS based on a JSON file
#
# Usage: python getLumi.py in.json
#
# Where the in.json is either a JSON file you get from CRAB by e.g. crab -report or a JSON listing the good runs from some other source
#
# The code requires lumi_by_LS.csv present in the current working directory. You can get the file from: 
#  https://twiki.cern.ch/twiki/bin/view/CMS/LumiWiki2010Data
# 

import json, csv, sys

my_lumi_json=file(sys.argv[1],'r')
my_lumi_dict = json.load(my_lumi_json)
official_lumi_json=file(sys.argv[2],'r')
official_lumi_dict = json.load(official_lumi_json)

# open the csv file

lumi_list_csv = open('lumi_by_LS.csv','rb')
# Skip first 5 lines, which are comments
for i in range(5):
	lumi_list_csv.next()

lumi_dict = csv.DictReader(lumi_list_csv,delimiter=',',fieldnames=['Run','LS','HFC','VTXC','HFL','VTXL'])
lumi = {}
for l in lumi_dict:
	kw="%d_%d" % (int(l['Run']),int(l['LS']))
	lumi[kw]=float(l['VTXL'])
	
tot=1e-30

# now get our json stuff

# compare our json with the official json

# store keywords for official json
kw_official_json = []
for k, v in official_lumi_dict.items():
  for lumis in v:
    if type(lumis) == type([]) and len(lumis) == 2:
      for i in range(lumis[0], lumis[1] + 1):
		kw="%d_%d" % (int(k),int(i))
		kw_official_json.append(kw)

# cross-check them with ours and fill the final dict
kw_final_json = []
for k, v in my_lumi_dict.items():
  for lumis in v:
    if type(lumis) == type([]) and len(lumis) == 2:
      for i in range(lumis[0], lumis[1] + 1):
		kw="%d_%d" % (int(k),int(i))
		if kw in kw_official_json:
			kw_final_json.append(kw)


print len(kw_official_json)
print len(kw_final_json)

for kw in kw_final_json:
	if kw in lumi:
		tot+=lumi[kw]

ll = tot / 4.29e+28

print "Total luminosity: %1.2f /ub, %1.2f /nb, %1.2e /pb, %1.2e /fb" % (ll,ll/1000,ll/1e+6,ll/1e+9)
