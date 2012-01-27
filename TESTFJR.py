# test suite

# for getting stuff from fjr files
#from fjrHandler import FJRHandler,GreenBoxHandler
#from xml.sax import make_parser

#from xml.sax.handler import ContentHandler

#file="CMSSW_4_1_4_patch4_TopTreeProd_41X_v4/src/ConfigurationFiles/WWtoAnything_TuneZ2_7TeV-pythia6-tauola/Spring11-PU_S1_START311_V1G1-v1/17062011_105711/TOPTREE_Spring11-PU_S1_START311_V1G1-v1_17062011_105711/res/crab_fjr_100.xml"

#parser = make_parser()
#handler = FJRHandler()
#parser.setContentHandler(handler)
#parser.parse(open(file))
#print handler.getEventsProcessed()
#print handler.getFrameworkExitCode().split("\n")[0]

from CrabHandler import CRABHandler
from logHandler import logHandler

crab = CRABHandler("1234567","CMSSW_4_1_4_patch4_TopTreeProd_41X_v4/src/ConfigurationFiles/WWtoAnything_TuneZ2_7TeV-pythia6-tauola/Spring11-PU_S1_START311_V1G1-v1/17062011_105711/",logHandler(""))

crab.UIWorkingDir="TOPTREE_Spring11-PU_S1_START311_V1G1-v1_17062011_105711"

crab.checkFJR()
