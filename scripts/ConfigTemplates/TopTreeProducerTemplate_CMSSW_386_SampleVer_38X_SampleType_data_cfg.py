import FWCore.ParameterSet.Config as cms
process = cms.Process("NewProcess")
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string('GR_R_38X_V13::All')
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.source = cms.Source("PoolSource",
fileNames = cms.untracked.vstring('file:06102010_120616_PAT.root'))
process.analysis = cms.EDAnalyzer("TopTreeProducer",
	myConfig = cms.PSet(
		dataType = cms.untracked.string("PAT"), 
		verbosity = cms.untracked.int32(0),
		RootFileName = cms.untracked.string('06102010_120616_TOPTREE.root'),
		doPDFInfo = cms.untracked.bool(False),
		doMC = cms.untracked.bool(False),
		doElectronMC = cms.untracked.bool(False),
		doMuonMC = cms.untracked.bool(False),
		doJetMC = cms.untracked.bool(False),
		doMETMC = cms.untracked.bool(False),
		doUnstablePartsMC = cms.untracked.bool(False),
		doSpinCorrGen = cms.untracked.bool(False),
		doSemiLepEvent = cms.untracked.bool(False),
		doHLT = cms.untracked.bool(True),
		doPrimaryVertex = cms.untracked.bool(True),
		doCaloJet = cms.untracked.bool(False),
		doCaloJetStudy = cms.untracked.bool(True),
		doCaloJetId = cms.untracked.bool(True),
		doPFJet = cms.untracked.bool(False),
		doPFJetStudy = cms.untracked.bool(True),
		doMuon = cms.untracked.bool(True),
		doCosmicMuon = cms.untracked.bool(False),
		doElectron = cms.untracked.bool(True),
		runGeneralTracks = cms.untracked.bool(True),
		runSuperCluster = cms.untracked.bool(True),
		doJPTJet = cms.untracked.bool(False),
		doJPTJetStudy = cms.untracked.bool(True),
		doCaloMET = cms.untracked.bool(True),
		doPFMET = cms.untracked.bool(True),
		doTCMET = cms.untracked.bool(True),
		doMHT = cms.untracked.bool(True),
		conversionLikelihoodWeightsFile = cms.untracked.string('RecoEgamma/EgammaTools/data/TMVAnalysis_Likelihood.weights.txt'),
	),
	producersNamesPAT = cms.PSet(
		dataType = cms.untracked.string("PAT"),
		hltProducer1st = cms.InputTag("TriggerResults","","HLT"),
		hltProducer2nd = cms.InputTag("TriggerResults","","REDIGI36X"),
		hltProducer8E29 = cms.InputTag("TriggerResults","","NONE"),
		genParticlesProducer = cms.InputTag("genParticles"),
		primaryVertexProducer = cms.InputTag("offlinePrimaryVertices"),
		caloJetProducer = cms.InputTag("selectedPatJetsAK5Calo"),
		pfJetProducer = cms.InputTag("selectedPatJetsPF"),
		vcaloJetProducer = cms.untracked.vstring("selectedPatJetsAK5Calo","selectedPatJetsIC5Calo","selectedPatJetsKT4Calo"),
		vpfJetProducer = cms.untracked.vstring("selectedPatJetsPF"),
		JPTJetProducer = cms.InputTag("selectedPatJetsAK5JPT"),
		vJPTJetProducer = cms.untracked.vstring("selectedPatJetsAK5JPT"),
		genJetProducer = cms.InputTag("ak5GenJets"),
		vgenJetProducer = cms.untracked.vstring("ak5GenJets","ak5GenJetsNoE"),
		muonProducer = cms.InputTag("selectedPatMuons"),
		electronProducer = cms.InputTag("cleanPatElectronsTriggerMatch"),
		CalometProducer = cms.InputTag("patMETs"),
		PFmetProducer = cms.InputTag("patMETsPF"),
		TCmetProducer = cms.InputTag("patMETsTC"),
		mhtProducer = cms.InputTag("patMHTs"),
		genEventProducer = cms.InputTag("genEvt"),
		electronNewId = cms.untracked.bool(False),
		generalTrackLabel = cms.InputTag("generalTracks"),
		electronTriggerMatching = cms.untracked.bool(True), # to keep the triggerMatching Info -- Only for PAT data type,
		electronTriggerPaths = cms.untracked.vstring('HLT_Ele10_SW_L1R','HLT_Ele15_SW_L1R')# for triggerMatching
	)
)
process.p = cms.Path(process.analysis)
