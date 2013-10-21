import FWCore.ParameterSet.Config as cms

process = cms.Process("NewProcess")

#keep the logging output to a nice level
process.load("FWCore.MessageLogger.MessageLogger_cfi")

process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")

# Global geometry
process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string('GR_R_41_V0::All')
# geometry needed for clustering and calo shapes variables
# process.load("RecoEcal.EgammaClusterProducers.geometryForClustering_cff")
# 3 folllowing config files included in RecoEcal.EgammaClusterProducers.geometryForClustering_cff
#process.load("Geometry.CMSCommonData.cmsIdealGeometryXML_cfi")
#process.load("Geometry.CaloEventSetup.CaloGeometry_cfi")
#process.load("Geometry.CaloEventSetup.CaloTopology_cfi")

# ES cluster for pi0 discrimination variables
#process.load("RecoEcal.EgammaClusterProducers.preshowerClusterShape_cfi")

# pi0 discrimination variables
#process.load("RecoEcal.EgammaClusterProducers.piZeroDiscriminators_cfi")

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

process.source = cms.Source("PoolSource",
#        duplicateCheckMode = cms.untracked.string('noDuplicateCheck'),
	fileNames = cms.untracked.vstring('file:test_42_Data_PAT.root')
#	fileNames = cms.untracked.vstring('file:test311X_PAT_genEvent.root')
	#fileNames = cms.untracked.vstring('/store/data/CRAFT09/Cosmics/RAW-RECO/SuperPointing-CRAFT09_R_V4_CosmicsSeq_v1/0009/763782DB-DCB9-DE11-A238-003048678B30.root')
	#fileNames = cms.untracked.vstring('file:/user/echabert/CMSSW/CMSSW_2_2_3/src/TopQuarkAnalysis/TopEventProducers/test/toto2.root')
#	fileNames = cms.untracked.vstring('dcap:///pnfs/iihe/cms/store/user/blyweert/temp/CRAFT09_RERECO/CRAFT09_SuperPointing_RERECO_CMSSW330_1.root')
)

# reduce verbosity
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(-1)

process.analysis = cms.EDAnalyzer("TopTreeProducer",
	myConfig = cms.PSet(
		# Verbosite
		# 		0 = muet
 		# 		1 = Number of evt every 100 evts
 		# 		2 = Give the functions executed & nof objects build per event
 		# 		3 = Liste of high level objects (jetss, muons, ...)
 		# 		4 = List of all  objects 
		# 		5 = Debug
 		verbosity = cms.untracked.int32(0),

		# used in the electron to see if the magneticfield is taken from DCS or from IDEALMAGFIELDRECORD
		isData = cms.untracked.bool(True),

		# name of output root file
		RootFileName = cms.untracked.string('test_424_data_TOPTREE.root'),

		# What is written to rootuple		    
		doHLT = cms.untracked.bool(True),
		doMC = cms.untracked.bool(False),
		doPDFInfo = cms.untracked.bool(False),
		signalGenerator = cms.untracked.string('PYTHIA'),
#		signalGenerator = cms.untracked.string('ALPGEN'),
#		signalGenerator = cms.untracked.string('MADGRAPH'),

		doElectronMC = cms.untracked.bool(False),
		doMuonMC = cms.untracked.bool(False),
		doJetMC = cms.untracked.bool(False),
		doMETMC = cms.untracked.bool(False),
		doUnstablePartsMC = cms.untracked.bool(False),
		doPrimaryVertex = cms.untracked.bool(True),
		runGeneralTracks = cms.untracked.bool(True),#true only if generalTracks are stored.
		doCaloJet = cms.untracked.bool(True),
		doGenJet = cms.untracked.bool(False),
		doCaloJetId = cms.untracked.bool(True),
		doPFJet = cms.untracked.bool(True),
		doJPTJet = cms.untracked.bool(True),
		doJPTJetId = cms.untracked.bool(True),
		doMuon = cms.untracked.bool(True),
		doElectron = cms.untracked.bool(True),
		runSuperCluster = cms.untracked.bool(True),#true only if SuperCluster are stored
		doCaloMET = cms.untracked.bool(True),
		doPFMET = cms.untracked.bool(True),
		doTCMET = cms.untracked.bool(True),
		doGenEvent = cms.untracked.bool(False),#put on False when running non-ttbar or when running toptree from reco
		doNPGenEvent = cms.untracked.bool(False),#put on True when running New Physics sample
		doSpinCorrGen = cms.untracked.bool(False),#put on True only if you need SpinCorrelation Variables
		doSemiLepEvent = cms.untracked.bool(False),#put on True only if you need TtSemiLeptonicEvent Collection exist in PAT-uples (L2)

		conversionLikelihoodWeightsFile = cms.untracked.string('RecoEgamma/EgammaTools/data/TMVAnalysis_Likelihood.weights.txt'),

		# Draw MC particle tree
		drawMCTree = cms.untracked.bool(False),
		mcTreePrintP4 = cms.untracked.bool(False),
		mcTreePrintPtEtaPhi = cms.untracked.bool(False),
		mcTreePrintVertex = cms.untracked.bool(False),
		mcTreePrintStatus = cms.untracked.bool(False),
		mcTreePrintIndex = cms.untracked.bool(False),
		mcTreeStatus = cms.untracked.vint32( 3 ),	# accepted status codes

	
		# MC particles acceptance cuts
		electronMC_etaMax = cms.double(3.0),
		electronMC_ptMin = cms.double(2.0),
		muonMC_etaMax = cms.double(3.0),
		muonMC_ptMin = cms.double(0.0),
		jetMC_etaMax = cms.double(6.0),
		jetMC_ptMin = cms.double(5.0),
	),

	producersNames = cms.PSet(
		hltProducer1st = cms.InputTag("TriggerResults","","HLT"),
		hltProducer2nd = cms.InputTag("TriggerResults","","RECO"),
		hltProducer3rd = cms.InputTag("TriggerResults","","REDIGI"),
		hltProducer4th = cms.InputTag("TriggerResults","","REDIGI311X"),
		pileUpProducer = cms.InputTag("addPileupInfo"),
		genParticlesProducer = cms.InputTag("genParticles"),
		primaryVertexProducer = cms.InputTag("goodOfflinePrimaryVertices"), #used everywhere in pat, logical to keep only these
		vcaloJetProducer = cms.untracked.vstring("selectedPatJetsAK5Calo"),
		vgenJetProducer = cms.untracked.vstring("ak5GenJets"),
		vpfJetProducer = cms.untracked.vstring("selectedPatJetsAK5PF","selectedPatJetsPF2PAT"),
		vJPTJetProducer = cms.untracked.vstring("selectedPatJetsAK5JPT"),
		vmuonProducer = cms.untracked.vstring("selectedPatMuons","selectedPatMuonsPF2PAT"),
		velectronProducer = cms.untracked.vstring("selectedPatElectrons","selectedPatElectronsPF2PAT"),# if electronTriggerMatching == true, change the electron inputTag to "cleanPatElectronsTriggerMatch"
		CalometProducer = cms.InputTag("patMETsAK5Calo"),
		PFmetProducer = cms.InputTag("patMETsPF2PAT"),
		TCmetProducer = cms.InputTag("patMETsTC"),
		genEventProducer = cms.InputTag("genEvt"),
		generalTrackLabel = cms.InputTag("generalTracks"),
		electronNewId = cms.untracked.bool(True) #for recent electronID recommended by EGamma. still Not accepted by Top group
	)
)

process.p = cms.Path(process.analysis)
