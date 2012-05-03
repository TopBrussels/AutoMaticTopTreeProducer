# Starting with a skeleton process which gets imported with the following line
from PhysicsTools.PatAlgos.patTemplate_cfg import *

from PhysicsTools.PatAlgos.tools.coreTools import *

process.source.fileNames = [
    '/store/mc/Summer12/DYToEE_M_20_TuneZ2star_8TeV_pythia6/AODSIM/PU_S7_START50_V15-v1/0000/3236025D-277E-E111-AA8A-00261894389E.root'
]

## import skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *

# load the PAT config
process.load("PhysicsTools.PatAlgos.patSequences_cff")


##################################
####### FIX FOR 51X Samples ######
##################################

from PhysicsTools.PatAlgos.tools.cmsswVersionTools import run52xOn51xTrigger
run52xOn51xTrigger( process )
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")

###############################
####### Global Setup ##########
###############################

process.load("FWCore.Framework.test.cmsExceptionsFatal_cff")
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load("PhysicsTools.HepMCCandAlgos.genParticles_cfi")
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.destinations = ['cerr']
process.MessageLogger.statistics = []
process.MessageLogger.fwkJobReports = []
process.MessageLogger.categories=cms.untracked.vstring('FwkJob'
							,'FwkReport'
							,'FwkSummary'
			                               )

process.MessageLogger.cerr.INFO = cms.untracked.PSet(limit = cms.untracked.int32(0))
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(100)
process.options = cms.untracked.PSet(
		                 wantSummary = cms.untracked.bool(True)
	         	 	)

process.GlobalTag.globaltag = cms.string('START52_V9::All')


##-------------------- Import the Jet RECO modules ----------------------- ## this makes cmsRun crash
##
#process.load('RecoJets.Configuration.RecoPFJets_cff')
##-------------------- Turn-on the FastJet density calculation -----------------------
process.kt6PFJets.doRhoFastjet = True
##-------------------- Turn-on the FastJet jet area calculation for your favorite algorithm -----------------------
#process.ak5PFJets.doAreaFastjet = True

process.primaryVertexFilter = cms.EDFilter("GoodVertexFilter",
                                           vertexCollection = cms.InputTag('offlinePrimaryVertices'),
                                           minimumNDOF = cms.uint32(4) ,
                                           maxAbsZ = cms.double(24), 
                                           maxd0 = cms.double(2) 
                                           )

from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector

process.goodOfflinePrimaryVertices = cms.EDFilter(
    "PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone( maxZ = cms.double(24.0) ),
    src=cms.InputTag('offlinePrimaryVertices')
    )

############################### 
########## Track Met ##########
###############################  

#process.load("RecoMET.METProducers.trackMET_cff")
#from RecoMET.METProducers.trackMET_cff import *
#process.recoTrackMET = cms.Sequence(
#process.pfCandidatesForTrackMet*process.trackMet )

###############################
#### Load MVA electron Id #####
###############################

process.load('EGamma.EGammaAnalysisTools.electronIdMVAProducer_cfi')
process.mvaTrigV0.mvaWeightFile = cms.vstring(
    "Electrons_BDTG_TrigV0_Cat1.weights.xml",
    "Electrons_BDTG_TrigV0_Cat2.weights.xml",
    "Electrons_BDTG_TrigV0_Cat3.weights.xml",
    "Electrons_BDTG_TrigV0_Cat4.weights.xml",
    "Electrons_BDTG_TrigV0_Cat5.weights.xml",
    "Electrons_BDTG_TrigV0_Cat6.weights.xml"
    )
process.mvaNonTrigV0.mvaWeightFile = cms.vstring(
    "Electrons_BDTG_NonTrigV0_Cat1.weights.xml",
    "Electrons_BDTG_NonTrigV0_Cat2.weights.xml",
    "Electrons_BDTG_NonTrigV0_Cat3.weights.xml",
    "Electrons_BDTG_NonTrigV0_Cat4.weights.xml",
    "Electrons_BDTG_NonTrigV0_Cat5.weights.xml",
    "Electrons_BDTG_NonTrigV0_Cat6.weights.xml"
    )
process.eidMVASequence = cms.Sequence( process.mvaTrigV0 + process.mvaNonTrigV0 )

###############################
####### PF2PAT Setup ##########
###############################

# Default PF2PAT with AK5 jets. Make sure to turn ON the L1fastjet stuff. 
from PhysicsTools.PatAlgos.tools.pfTools import *
postfix = "PF2PAT"
usePF2PAT(process,runPF2PAT=True, jetAlgo="AK5", runOnMC=True, postfix=postfix)

process.pfPileUpPF2PAT.Enable = True
process.pfPileUpPF2PAT.Vertices = 'goodOfflinePrimaryVertices' #added
process.pfJetsPF2PAT.doAreaFastjet = True
process.pfJetsPF2PAT.doRhoFastjet = False

process.pfIsolatedMuonsPF2PAT.combinedIsolationCut = cms.double(0.2)
process.pfIsolatedMuonsPF2PAT.isolationCut = cms.double(0.2)
process.pfIsolatedMuonsPF2PAT.doDeltaBetaCorrection = True
process.pfSelectedMuonsPF2PAT.cut = cms.string('pt > 10. && abs(eta) < 2.5')
process.pfIsolatedMuonsPF2PAT.isolationValueMapsCharged = cms.VInputTag(cms.InputTag("muPFIsoValueCharged03PF2PAT"))
process.pfIsolatedMuonsPF2PAT.deltaBetaIsolationValueMap = cms.InputTag("muPFIsoValuePU03PF2PAT")
process.pfIsolatedMuonsPF2PAT.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("muPFIsoValueNeutral03PF2PAT"), cms.InputTag("muPFIsoValueGamma03PF2PAT"))

print "process.pfIsolatedMuonsPF2PAT.isolationCut -> "+str(process.pfIsolatedMuonsPF2PAT.isolationCut)
print "process.pfIsolatedMuonsPF2PAT.combinedIsolationCut -> "+str(process.pfIsolatedMuonsPF2PAT.combinedIsolationCut)

process.pfIsolatedElectronsPF2PAT.combinedIsolationCut = cms.double(0.2)
process.pfIsolatedElectronsPF2PAT.isolationCut = cms.double(0.2)

process.pfIsolatedElectronsPF2PAT.doDeltaBetaCorrection = True

process.pfSelectedElectronsPF2PAT.cut = cms.string('pt > 15. && abs(eta) < 2.5')
process.pfIsolatedElectronsPF2PAT.isolationValueMapsCharged = cms.VInputTag(cms.InputTag("elPFIsoValueCharged03PFIdPF2PAT"))
process.pfIsolatedElectronsPF2PAT.deltaBetaIsolationValueMap = cms.InputTag("elPFIsoValuePU03PFIdPF2PAT")
process.pfIsolatedElectronsPF2PAT.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("elPFIsoValueNeutral03PFIdPF2PAT"), cms.InputTag("elPFIsoValueGamma03PFIdPF2PAT"))

process.patElectronsPF2PAT.isolationValues = cms.PSet(
    pfChargedHadrons = cms.InputTag("elPFIsoValueCharged03PFIdPF2PAT"),
    pfChargedAll = cms.InputTag("elPFIsoValueChargedAll03PFIdPF2PAT"),
    pfPUChargedHadrons = cms.InputTag("elPFIsoValuePU03PFIdPF2PAT"),
    pfNeutralHadrons = cms.InputTag("elPFIsoValueNeutral03PFIdPF2PAT"),
    pfPhotons = cms.InputTag("elPFIsoValueGamma03PFIdPF2PAT")
    )

process.patElectronsPF2PAT.electronIDSources.mvaTrigV0    = cms.InputTag("mvaTrigV0")
process.patElectronsPF2PAT.electronIDSources.mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0") 

process.patPF2PATSequencePF2PAT.replace( process.patElectronsPF2PAT, process.eidMVASequence * process.patElectronsPF2PAT )

process.patJetCorrFactorsPF2PAT.payload = 'AK5PFchs'
process.patJetCorrFactorsPF2PAT.levels = cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute'])
process.patJetCorrFactorsPF2PAT.rho = cms.InputTag("kt6PFJetsPF2PAT", "rho")
process.pfPileUpPF2PAT.checkClosestZVertex = False

# Use the good primary vertices everywhere. 
for imod in [process.patMuonsPF2PAT, process.patElectronsPF2PAT] :
    imod.pvSrc = "goodOfflinePrimaryVertices"
    imod.embedTrack = cms.bool(True)
    
# top projections in PF2PAT:
getattr(process,"pfNoPileUp"+postfix).enable = True
getattr(process,"pfNoMuon"+postfix).enable = True
getattr(process,"pfNoElectron"+postfix).enable = True
getattr(process,"pfNoTau"+postfix).enable = False
getattr(process,"pfNoJet"+postfix).enable = False

#print "OLD DZ CUT: "+str(getattr(process,"pfMuonsFromVertexPF2PAT").dzCut)

#getattr(process,"pfMuonsFromVertexPF2PAT").dzCut = 99
#getattr(process,"pfMuonsFromVertexPF2PAT").d0Cut = 99
#getattr(process,"pfSelectedMuonsPF2PAT").cut="pt()>3"

#getattr(process,"pfNoMuon"+postfix).enable = False
#getattr(process,"pfNoElectron"+postfix).enable = False 
#getattr(process,"pfNoTau"+postfix).enable = False 
#getattr(process,"pfNoJet"+postfix).enable = True
#getattr(process,"pfIsolatedMuons"+postfix).isolationCut = 999999
#getattr(process,"pfIsolatedElectrons"+postfix).isolationCut = 999999

################################################################
#### Clone the PF2PAT sequence for data-driven QCD estimate ####
################################################################

from PhysicsTools.PatAlgos.tools.helpers import cloneProcessingSnippet
postfixNoLeptonCleaning = 'NoLeptonCleaning'

# just cloning the first sequence, and enabling lepton cleaning 
cloneProcessingSnippet(process, getattr(process, 'patPF2PATSequencePF2PAT'), postfixNoLeptonCleaning)

getattr(process,"pfNoMuonPF2PATNoLeptonCleaning").enable = False
getattr(process,"pfNoElectronPF2PATNoLeptonCleaning").enable = False 
getattr(process,"pfIsolatedMuonsPF2PATNoLeptonCleaning").combinedIsolationCut = cms.double(999999)
getattr(process,"pfIsolatedMuonsPF2PATNoLeptonCleaning").isolationCut = cms.double(999999)
getattr(process,"pfIsolatedElectronsPF2PATNoLeptonCleaning").combinedIsolationCut = cms.double(999999)
getattr(process,"pfIsolatedElectronsPF2PATNoLeptonCleaning").isolationCut = cms.double(999999)

###############################
### TagInfo and Matching Setup#
###############################

#process.patJetsPF2PAT.embedGenJetMatch = True
#process.patJetsPF2PAT.getJetMCFlavour = True
#process.patJetsPF2PAT.addGenPartonMatch = True
# Add the calo towers and PFCandidates.
process.patJetsPF2PAT.embedCaloTowers = True
process.patJetsPF2PAT.embedPFCandidates = True
process.patJetsPF2PAT.tagInfoSources = cms.VInputTag( cms.InputTag("secondaryVertexTagInfosAODPF2PAT") )

###############################
###### Bare KT 0.6 jets #######
###############################

from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
process.kt6PFJetsPF2PAT = kt4PFJets.clone(
    rParam = cms.double(0.6),
    #src = cms.InputTag('pfNoElectronPF2PAT'),
    doAreaFastjet = cms.bool(True),
    doRhoFastjet = cms.bool(True)
    )

getattr(process,"patPF2PATSequencePF2PAT").replace( getattr(process,"pfNoElectronPF2PAT"), getattr(process,"pfNoElectronPF2PAT")*getattr(process,"kt6PFJetsPF2PAT") )

# For electron (effective area) isolation
process.kt6PFJetsForIsolation = kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
process.kt6PFJetsForIsolation.Rho_EtaMax = cms.double(2.5)

###############################
#### Selections Setup #########
###############################

# AK5 Jets
#   PF
process.selectedPatJetsPF2PAT.cut = cms.string("pt > 10")

# Flavor history stuff
process.load("PhysicsTools.HepMCCandAlgos.flavorHistoryPaths_cfi")
process.flavorHistoryFilter.pathToSelect = cms.int32(-1)

###############################
#### TYPE 1 MET correction ####
###############################

#(/afs/cern.ch/user/l/lacroix/public/Mara/patTuple_42x_jec_cfg.py was recommended as example in the MET WorkBook)

#process.load("PhysicsTools.PatUtils.patPFMETCorrections_cff")

# for main PF2PAT products
#process.selectedPatJetsForMETtype1p2Corr.src = cms.InputTag('selectedPatJetsPF2PAT')
#process.selectedPatJetsForMETtype2Corr.src = cms.InputTag('selectedPatJetsPF2PAT')
#process.patPFJetMETtype1p2Corr.type1JetPtThreshold = cms.double(10.0)
#process.patPFJetMETtype1p2Corr.skipEM = cms.bool(False)
#process.patPFJetMETtype1p2Corr.skipMuons = cms.bool(False)

# for non lepton-iso PF2PAT

#cloneProcessingSnippet(process, getattr(process, 'producePatPFMETCorrections'), postfixNoLeptonCleaning)

#getattr(process,"selectedPatJetsForMETtype1p2Corr"+postfixNoLeptonCleaning).src = cms.InputTag('selectedPatJetsPF2PAT'+postfixNoLeptonCleaning)
#getattr(process,"selectedPatJetsForMETtype2Corr"+postfixNoLeptonCleaning).src = cms.InputTag('selectedPatJetsPF2PAT'+postfixNoLeptonCleaning)
#getattr(process,"patPFJetMETtype1p2Corr"+postfixNoLeptonCleaning).type1JetPtThreshold = cms.double(10.0)
#getattr(process,"patPFJetMETtype1p2Corr"+postfixNoLeptonCleaning).skipEM = cms.bool(False)
#getattr(process,"patPFJetMETtype1p2Corr"+postfixNoLeptonCleaning).skipMuons = cms.bool(False)

# let it run

process.patseq = cms.Sequence(
    process.kt6PFJets*
    process.kt6PFJetsForIsolation*
    process.goodOfflinePrimaryVertices* 
    process.primaryVertexFilter * #removes events with no good pv (but if cuts to determine good pv change...)
    getattr(process,"patPF2PATSequence"+postfix)* # main PF2PAT
    getattr(process,"patPF2PATSequence"+postfix+postfixNoLeptonCleaning)* # PF2PAT FOR DATA_DRIVEN QCD
    process.flavorHistorySeq
    )

####################################
#### ENERGY CONSERVATION FILTER ####
####################################

# SHOULD NOT BE USED ON 2012 MC ACCORDING TO TOP REFSEL TWIKI
#process.load("GeneratorInterface.GenFilters.TotalKinematicsFilter_cfi")
#process.totalKinematicsFilter.tolerance = 5. # recommended, default: 0.5
    
#################
#### ENDPATH ####
#################

process.p = cms.Path(
    #process.totalKinematicsFilter*
    process.PFTau * # 51X samples fix
    process.patseq#*process.producePatPFMETCorrections*getattr(process, 'producePatPFMETCorrections'+postfixNoLeptonCleaning)
    )

process.out.SelectEvents.SelectEvents = cms.vstring('p')

# rename output file
process.out.fileName = "MC_Summer12_PAT.root"

# process all the events
process.maxEvents.input = -1 #changed

#process.source.skipEvents = cms.untracked.uint32(6049)
#process.source.skipEvents = cms.untracked.uint32(850)
#process.source.skipEvents = cms.untracked.uint32(8123)

process.options.wantSummary = False
process.out.dropMetaData = cms.untracked.string("DROPPED")

process.source.inputCommands = cms.untracked.vstring("keep *", "drop *_MEtoEDMConverter_*_*")

process.out.outputCommands = [
    'drop *_cleanPat*_*_*',
    'keep *_selectedPat*_*_*',
    'keep *_goodPat*_*_*',
    'keep patJets_*_*_*',
    'keep *_patMETs*_*_*',
    'keep *_patType1CorrectedPFMet*_*_*',
    'keep *_goodOfflinePrimaryVertices*_*_*',    
    'drop patPFParticles_*_*_*',
    'drop patTaus_*_*_*',
    'keep double_*PF2PAT*_*_PAT',
    'keep double_kt6PFJetsForIsolation_rho_*',
    'keep *_TriggerResults_*_*',
    'keep *_hltTriggerSummaryAOD_*_*',
    'keep *_ak5GenJets*_*_*',
    'keep double_genEvent*_*_*',
    'keep TtGenEvent_*_*_*',
    'keep GenRunInfoProduct_generator_*_*',
    'keep GenEventInfoProduct_generator_*_*',
    'keep *_genEventWeight_*_*',
    'keep *_bFlavorHistoryProducer_*_*',
    'keep *_cFlavorHistoryProducer_*_*',
    'keep *_flavorHistoryFilter_*_*',
    'keep PileupSummaryInfos_*_*_*',
    'keep recoTracks_generalTracks_*_*',
    'keep recoPFCandidates_selectedPatJets*_*_*',
    'keep recoBaseTagInfosOwned_selectedPatJets*_*_*',
    'keep CaloTowers_selectedPatJets*_*_*',
    'keep *_*genParticles*_*_*',
    'keep recoGenParticles_*_*_*',
    'keep *_offlineBeamSpot_*_*',
    'keep recoCaloClusters_*_*_*',
    'keep *_reducedEcalRecHits*_*_*',
    'keep edmHepMC*_*_*_*',
    'keep recoPdfinfo_*_*_*',
    'keep triggerTriggerEvent_*_*_*',
    'keep GenEventInfoProduct_*_*_*',
    'keep DcsStatuss_scalersRawToDigi__*',
    'drop *_selectedPatJets_*_*',
    'drop *_patMETs_*_*',
    'drop *_selectedPatPhotons*_*_*'
    ]
