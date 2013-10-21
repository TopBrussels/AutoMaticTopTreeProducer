## import skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *

process.MessageLogger.cerr.FwkReport.reportEvery = 100

## ------------------------------------------------------
#  NOTE: you can use a bunch of core tools of PAT to
#  taylor your PAT configuration; for a few examples
#  uncomment the lines below
## ------------------------------------------------------
from PhysicsTools.PatAlgos.tools.coreTools import *

## remove MC matching from the default sequence
removeMCMatching(process)
runOnData(process)

## remove certain objects from the default sequence
# removeAllPATObjectsBut(process, ['Muons'])
# removeSpecificPATObjects(process, ['Electrons', 'Muons', 'Taus'])

process.load("CommonTools/RecoAlgos/HBHENoiseFilter_cfi")

process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")

from PhysicsTools.PatAlgos.tools.muonTools import addMuonUserIsolation

addMuonUserIsolation(process)

## uncomment the following line to add tcMET to the event content
from PhysicsTools.PatAlgos.tools.metTools import *
addTcMET(process, 'TC')
addPfMET(process, 'PF')

## uncomment the following line to add different jet collections
## to the event content
from PhysicsTools.PatAlgos.tools.jetTools import *

##-------------------- Import the JEC services -----------------------
process.load('JetMETCorrections.Configuration.DefaultJEC_cff')
##-------------------- Disable the CondDB for the L1Offset (until they are included in a new global tag) -------
process.ak5CaloL1Offset.useCondDB = False
process.ak5PFL1Offset.useCondDB = False
process.ak5JPTL1Offset.useCondDB = False

addJetCollection(process,cms.InputTag('JetPlusTrackZSPCorJetAntiKt5'),
                 'AK5', 'JPT',
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5JPT', cms.vstring(['L1Offset', 'L2Relative', 'L3Absolute', 'L2L3Residual'])),
                 doType1MET   = False,
                 doL1Cleaning = False,
                 doL1Counters = True,                 
                 genJetCollection = cms.InputTag("ak5GenJets"),
                 doJetID      = True,
                 jetIdLabel   = "ak5"
                 )

addJetCollection(process,cms.InputTag('ak5CaloJets'),
                 'AK5', 'Calo',
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5Calo', cms.vstring(['L1Offset', 'L2Relative', 'L3Absolute', 'L2L3Residual'])),
                 doType1MET   = True,                            
                  doL1Cleaning = True,
                 doL1Counters = False,
                 genJetCollection=cms.InputTag("ak5GenJets"),
                 doJetID      = True,
                 jetIdLabel   = "ak5",
                 )

addJetCollection(process,cms.InputTag('ak5PFJets'),
                 'AK5', 'PF',
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5PF', cms.vstring(['L1Offset', 'L2Relative', 'L3Absolute', 'L2L3Residual'])),
                 doType1MET   = False,                            
                 doL1Cleaning = True,
                 doL1Counters = False,
                 genJetCollection=cms.InputTag("ak5GenJets"),
                 doJetID      = True,
                 jetIdLabel   = "ak5",
                 )

# Configure PAT to use PF2PAT instead of AOD sources
# this function will modify the PAT sequences. It is currently
# not possible to run PF2PAT+PAT and standart PAT at the same time
#from PhysicsTools.PatAlgos.tools.pfTools import *
# An empty postfix means that only PF2PAT is run,  
# otherwise both standard PAT and PF2PAT are run. In the latter case PF2PAT
# collections have standard names + postfix (e.g. patElectronPFlow)
#postfix = "PF"
#usePF2PAT(process,runPF2PAT=True, jetAlgo='AK5', runOnMC=True, postfix=postfix)


## let it run
process.p = cms.Path(process.HBHENoiseFilter *   
cms.Sequence(
	process.PFTau * #needed to avoid crash due to some missing reference
  process.jetTracksAssociatorAtVertexAK5JPT*
  process.jetTracksAssociatorAtVertexAK5Calo*
  process.jetTracksAssociatorAtVertexAK5PF*
  process.btaggingAK5JPT *
  process.btaggingAK5Calo *
  process.btaggingAK5PF *
	process.patDefaultSequence
	)
)


## ------------------------------------------------------
#  In addition you usually want to change the following
#  parameters:
## ------------------------------------------------------
#
process.GlobalTag.globaltag =  cms.string('GR_R_311_V2::All')     ##  (according to https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideFrontierConditions)
#                                         ##
process.source.fileNames = [          ##
'file:/user/mmaes/311XData.root'
]                                     ##  (e.g. 'file:AOD.root')
#                                         ##
process.maxEvents.input = 100         ##  (e.g. -1 to run on all events)
#                                         ##
#   process.out.outputCommands = [ ... ]  ##  (e.g. taken from PhysicsTools/PatAlgos/python/patEventContent_cff.py)
#                                         ##
process.out.outputCommands.extend(cms.vstring("keep *_selected*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep double_genEvent*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep edmHepMC*_*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep recoGenParticles_*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep recoPdfinfo_*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep recoTracks_generalTracks_*_*"))
process.out.outputCommands.extend(cms.vstring("keep triggerTriggerEvent_*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep edmTriggerResults_*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep recoVertexs_offlinePrimaryVertices_*_*"))
process.out.outputCommands.extend(cms.vstring("keep recoBeamSpot_offlineBeamSpot_*_*"))
process.out.outputCommands.extend(cms.vstring("keep CaloTowersSorted_towerMaker_*_*"))
process.out.outputCommands.extend(cms.vstring("keep CaloTowersSorted_cleanTowers_*_*"))
process.out.outputCommands.extend(cms.vstring("keep recoCaloClusters_*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep recoPFCandidates_particleFlow_*_*"))
process.out.outputCommands.extend(cms.vstring("keep recoGsfElectronCores_*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep recoGenJets_ak5GenJets*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep TtGenEvent_*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop *_*CaloPF*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop *_*JPTPF*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop *_*PFPF*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop patPhotons_*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop patTaus_*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop patMHTs_*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop patMETs_*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop patJets_selectedPatJets__PAT"))
process.out.outputCommands.extend(cms.vstring("drop *_cleanPat*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep patMETs_patMETs*__PAT"))
process.out.outputCommands.extend(cms.vstring("keep patMHTs_patMHTs__PAT"))
process.out.outputCommands.extend(cms.vstring("keep *_cleanPatElectronsTriggerMatch_*_*"))
process.out.outputCommands.extend(cms.vstring("keep DcsStatuss_scalersRawToDigi_*_*"))
process.out.outputCommands.extend(cms.vstring("keep GenEventInfoProduct_*_*_*"))

process.out.fileName = cms.untracked.string('test311X_PAT_data.root')            ##  (e.g. 'myTuple.root')
#                                         ##
process.options.wantSummary = False    ##  (to suppress the long output at the end of the job)    
