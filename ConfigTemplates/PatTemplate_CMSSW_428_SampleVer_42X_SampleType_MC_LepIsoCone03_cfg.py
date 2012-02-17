# Starting with a skeleton process which gets imported with the following line
import FWCore.ParameterSet.Config as cms

from PhysicsTools.PatAlgos.patTemplate_cfg import *

from PhysicsTools.PatAlgos.tools.coreTools import *

process.source.fileNames = [
"/store/mc/Fall11/TTJets_TuneZ2_7TeV-madgraph-tauola/AODSIM/PU_S6_START42_V14B-v1/0000/380EDCD0-CFFA-E011-8B63-002618943834.root"

]

###############################
####### Global Setup ##########
###############################

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load('FWCore.MessageService.MessageLogger_cfi')
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
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(10)
process.options = cms.untracked.PSet(
		                 wantSummary = cms.untracked.bool(True)
	         	 	)


process.GlobalTag.globaltag = cms.string('START42_V17::All') #new (11 Jan 2012) JEC

process.GlobalTag.toGet = cms.VPSet(
  cms.PSet(record = cms.string("BTagTrackProbability2DRcd"),
       tag = cms.string("TrackProbabilityCalibration_2D_2011_v1_mc"),
       connect = cms.untracked.string("frontier://FrontierProd/CMS_COND_31X_BTAU")),
  cms.PSet(record = cms.string("BTagTrackProbability3DRcd"),
       tag = cms.string("TrackProbabilityCalibration_3D_2011_v1_mc"),
       connect = cms.untracked.string("frontier://FrontierProd/CMS_COND_31X_BTAU"))
)

##-------------------- Import the Jet RECO modules -----------------------
process.load('RecoJets.Configuration.RecoPFJets_cff')
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
########## Electron ID ########
###############################
  
process.load('RecoEgamma.ElectronIdentification.cutsInCategoriesElectronIdentificationV06_cfi')
process.load("ElectroWeakAnalysis.WENu.simpleEleIdSequence_cff")

process.patElectrons.electronIDSources = cms.PSet(
    #CiC
    eidVeryLooseMC = cms.InputTag("eidVeryLooseMC"),
    eidLooseMC = cms.InputTag("eidLooseMC"),
    eidMediumMC = cms.InputTag("eidMediumMC"),
    eidTightMC = cms.InputTag("eidTightMC"),
    eidSuperTightMC = cms.InputTag("eidSuperTightMC"),
    eidHyperTight1MC = cms.InputTag("eidHyperTight1MC"),
    #VBTF 2010
    simpleEleId95relIso= cms.InputTag("simpleEleId95relIso"),
    simpleEleId90relIso= cms.InputTag("simpleEleId90relIso"),
    simpleEleId85relIso= cms.InputTag("simpleEleId85relIso"),
    simpleEleId80relIso= cms.InputTag("simpleEleId80relIso"),
    simpleEleId70relIso= cms.InputTag("simpleEleId70relIso"),
    simpleEleId60relIso= cms.InputTag("simpleEleId60relIso"),
    #Old selections
    eidRobustLoose = cms.InputTag("eidRobustLoose"),
    eidRobustTight = cms.InputTag("eidRobustTight"),
    eidRobustHighEnergy = cms.InputTag("eidRobustHighEnergy"),
    eidLoose  = cms.InputTag("eidLoose"), 
    eidTight = cms.InputTag("eidTight"),
       
)

process.patElectronIDs = cms.Sequence(process.simpleEleIdSequence)
process.eidCiCSequence = cms.Sequence(
    process.eidVeryLooseMC * process.eidLooseMC * process.eidMediumMC
  * process.eidTightMC * process.eidSuperTightMC * process.eidHyperTight1MC
)




############################### 
########## Track Met ##########
###############################  

process.load("RecoMET.METProducers.trackMET_cff")
from RecoMET.METProducers.trackMET_cff import *
process.recoTrackMET = cms.Sequence(
process.pfCandidatesForTrackMet*process.trackMet )


############################### 
########## Gen Setup ##########
###############################  
    
#process.load("RecoJets.Configuration.GenJetParticles_cff")
                
process.load("TopQuarkAnalysis.TopEventProducers.sequences.ttGenEvent_cff")
                
###############################
####### PF2PAT Setup ##########
###############################

# Default PF2PAT with AK5 jets. Make sure to turn ON the L1fastjet stuff. 
from PhysicsTools.PatAlgos.tools.pfTools import *
postfix = "PF2PAT"
usePF2PAT(process,runPF2PAT=True, jetAlgo='AK5', runOnMC=True, postfix=postfix)
process.pfPileUpPF2PAT.Enable = True
process.pfPileUpPF2PAT.Vertices = 'goodOfflinePrimaryVertices' #added
process.pfJetsPF2PAT.doAreaFastjet = True
process.pfJetsPF2PAT.doRhoFastjet = False

process.pfIsolatedMuonsPF2PAT.combinedIsolationCut = cms.double(0.2)
process.pfSelectedMuonsPF2PAT.cut = cms.string('pt > 10. && abs(eta) < 2.5')
#process.pfMuonsFromVertexPF2PAT.vertices = cms.InputTag("goodOfflinePrimaryVertices")
process.pfIsolatedElectronsPF2PAT.combinedIsolationCut = cms.double(0.2)
process.pfSelectedElectronsPF2PAT.cut = cms.string('et > 15. && abs(eta) < 2.5')
#process.pfElectronsFromVertexPF2PAT.vertices = cms.InputTag("goodOfflinePrimaryVertices")

process.patJetCorrFactorsPF2PAT.payload = 'AK5PFchs'
process.patJetCorrFactorsPF2PAT.levels = cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute'])
process.patJetCorrFactorsPF2PAT.rho = cms.InputTag("kt6PFJetsPF2PAT", "rho")
process.pfPileUpPF2PAT.checkClosestZVertex = False

applyPostfix( process, 'pfNoJet' , postfix ).enable = False
applyPostfix( process, 'pfNoTau' , postfix ).enable = False

# Use the good primary vertices everywhere. 
for imod in [process.patMuonsPF2PAT, process.patElectronsPF2PAT] :
    imod.pvSrc = "goodOfflinePrimaryVertices"
    imod.embedTrack = cms.bool(True)


###############################
### PF isolation cone#
###############################
#muons
applyPostfix(process,"isoValMuonWithNeutral",postfix).deposits[0].deltaR = cms.double(0.3)
applyPostfix(process,"isoValMuonWithCharged",postfix).deposits[0].deltaR = cms.double(0.3)
applyPostfix(process,"isoValMuonWithPhotons",postfix).deposits[0].deltaR = cms.double(0.3)
#electrons
applyPostfix(process,"isoValElectronWithNeutral",postfix).deposits[0].deltaR = cms.double(0.3)
applyPostfix(process,"isoValElectronWithCharged",postfix).deposits[0].deltaR = cms.double(0.3)
applyPostfix(process,"isoValElectronWithPhotons",postfix).deposits[0].deltaR = cms.double(0.3)



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
    src = cms.InputTag('pfNoElectronPF2PAT'),
    doAreaFastjet = cms.bool(True),
    doRhoFastjet = cms.bool(True)
    )

getattr(process,"patPF2PATSequencePF2PAT").replace( getattr(process,"pfNoElectronPF2PAT"), getattr(process,"pfNoElectronPF2PAT")*getattr(process,"kt6PFJetsPF2PAT") )


# addJetCollection stuff		
#from PhysicsTools.PatAlgos.tools.jetTools import *

#addJetCollection(process,cms.InputTag('ak5PFJets'),
#                 'AK5', 'PF',
#                 doJTA        = True,
#                 doBTagging   = True,
#                 jetCorrLabel = ('AK5PF', cms.vstring(['L1Offset', 'L2Relative', 'L3Absolute'])),
#                 doType1MET   = False,                            
#                 doL1Cleaning = False,
#                 doL1Counters = False,
#                 genJetCollection=cms.InputTag("ak5GenJets"),
#                 doJetID      = True,
#                 jetIdLabel   = "ak5",
#                 )


###############################
#### Selections Setup #########
###############################

# AK5 Jets
#   PF
process.selectedPatJetsPF2PAT.cut = cms.string("pt > 10")
#process.selectedPatJetsAK5PF.cut = cms.string("pt > 10")

# Flavor history stuff
process.load("PhysicsTools.HepMCCandAlgos.flavorHistoryPaths_cfi")
process.flavorHistoryFilter.pathToSelect = cms.int32(-1)

#for type 1 MET correction (/afs/cern.ch/user/l/lacroix/public/Mara/patTuple_42x_jec_cfg.py was recommended as example in the MET WorkBook)
process.load("PhysicsTools.PatUtils.patPFMETCorrections_cff")
process.selectedPatJetsForMETtype1p2Corr.src = cms.InputTag('selectedPatJetsPF2PAT')
process.selectedPatJetsForMETtype2Corr.src = cms.InputTag('selectedPatJetsPF2PAT')
process.patPFJetMETtype1p2Corr.type1JetPtThreshold = cms.double(10.0)
process.patPFJetMETtype1p2Corr.skipEM = cms.bool(False)
process.patPFJetMETtype1p2Corr.skipMuons = cms.bool(False)



# let it run

process.patseq = cms.Sequence(
		process.kt6PFJets*
#		process.ak5PFJets*
	        process.goodOfflinePrimaryVertices* 
                process.primaryVertexFilter * #removes events with no good pv (but if cuts to determine good pv change...)
                process.patElectronIDs*
		process.eidCiCSequence*
                getattr(process,"patPF2PATSequence"+postfix)*
#               process.patDefaultSequence*
		process.flavorHistorySeq#*
		
#    process.makeGenEvt
    )

process.printEvents = cms.EDAnalyzer("ParticleListDrawer",
		   src=cms.InputTag("genParticles"),
		      maxEventsToPrint = cms.untracked.int32(1)
		      )

process.totalKinematicsFilter = cms.EDFilter('TotalKinematicsFilter',
		  src             = cms.InputTag("genParticles"),
		    MHTSource       = cms.InputTag("mhtPF"),
		      tolerance       = cms.double(0.5),
		        verbose         = cms.untracked.bool(False)
			)



process.p0 = cms.Path(
    process.totalKinematicsFilter*process.printEvents*process.recoTrackMET*process.patseq*process.producePatPFMETCorrections
    )

process.out.SelectEvents.SelectEvents = cms.vstring('p0')
    
# rename output file
process.out.fileName = "TTJets_Madgraph_Fall11_42_PAT_MC_TEST.root"

# reduce verbosity
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(100)


# process all the events
process.maxEvents.input = 100
process.options.wantSummary = True
process.out.dropMetaData = cms.untracked.string("DROPPED")

process.source.inputCommands = cms.untracked.vstring("keep *", "drop *_MEtoEDMConverter_*_*")

process.out.outputCommands = [
    'drop *_cleanPat*_*_*',
    'keep *_selectedPat*_*_*',
    'keep *_goodPat*_*_*',
    'keep patJets_*_*_*',
    'keep *_patMETs*_*_*',
    'keep *_patType1CorrectedPFMet_*_*',
    'keep *_trackMet_*_*',
    'keep *_offlinePrimaryVertices*_*_*',
    'keep *_goodOfflinePrimaryVertices*_*_*',    
    'drop patPFParticles_*_*_*',
    'drop patTaus_*_*_*',
    'keep double_*PF2PAT*_*_PAT',
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
		'keep edmHepMC*_*_*_*',
		'keep recoPdfinfo_*_*_*',
		'keep triggerTriggerEvent_*_*_*',
		'keep GenEventInfoProduct_*_*_*',
		'keep DcsStatuss_scalersRawToDigi__*',
    'drop *_selectedPatJets_*_*',
		'drop *_patMETs_*_*',
		'drop *_selectedPatPhotons*_*_*'
    ]
