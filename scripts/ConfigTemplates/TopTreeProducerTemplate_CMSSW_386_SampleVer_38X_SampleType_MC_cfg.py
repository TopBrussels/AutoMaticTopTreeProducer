import FWCore.ParameterSet.Config as cms
process = cms.Process("NewProcess")
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string('START38_V13::All')
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.source = cms.Source("PoolSource",fileNames = cms.untracked.vstring('file:14032011_115034_PAT.root'))
process.analysis = cms.EDAnalyzer("TopTreeProducer",
	myConfig = cms.PSet(
		dataType = cms.untracked.string("PAT"), 
		verbosity = cms.untracked.int32(0),
		RootFileName = cms.untracked.string('14032011_115034_TOPTREE.root'),
		isData = cms.untracked.bool(False),
		doPDFInfo = cms.untracked.bool(False),
		signalGenerator = cms.untracked.string('PYTHIA'),
		doMC = cms.untracked.bool(True),
		doElectronMC = cms.untracked.bool(False),
		doMuonMC = cms.untracked.bool(True),
		doJetMC = cms.untracked.bool(True),
		doMETMC = cms.untracked.bool(True),
		doUnstablePartsMC = cms.untracked.bool(True),
		doNPGenEvent = cms.untracked.bool(True),
		doGenJet = cms.untracked.bool(True),
		doGenJetStudy = cms.untracked.bool(True),
		doGenEvent = cms.untracked.bool(False),
		doSpinCorrGen = cms.untracked.bool(False),
		doSemiLepEvent = cms.untracked.bool(False),
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
		doHLT = cms.untracked.bool(True),
		doHLT8E29 = cms.untracked.bool(True),
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
		runSuperCluster = cms.untracked.bool(False),
		doJPJet = cms.untracked.bool(False),
		doJPTJetStudy = cms.untracked.bool(True),
		doJPTJetId = cms.untracked.bool(True),
		doCaloMET = cms.untracked.bool(True),
		doPFMET = cms.untracked.bool(True),
		doTCMET = cms.untracked.bool(True),
		doMHT = cms.untracked.bool(True),
		conversionLikelihoodWeightsFile = cms.untracked.string('RecoEgamma/EgammaTools/data/TMVAnalysis_Likelihood.weights.txt'),
	),
	producersNamesPAT = cms.PSet(
		dataType = cms.untracked.string("PAT"),
		hltProducer1st = cms.InputTag("TriggerResults","","REDIGI38X"),
		hltProducer2nd = cms.InputTag("TriggerResults","","HLT"),
		hltProducer8E29 = cms.InputTag("TriggerResults","","RECO"),
		genParticlesProducer = cms.InputTag("genParticles"),
		primaryVertexProducer = cms.InputTag("offlinePrimaryVertices"),
		caloJetProducer = cms.InputTag("selectedPatJetsAK5Calo"),
		pfJetProducer = cms.InputTag("selectedPatJetsPF"),
		vcaloJetProducer = cms.untracked.vstring("selectedPatJetsAK5Calo","selectedPatJetsKT4Calo",'selectedPatJetsCleanedAK5Calo'),
		vpfJetProducer = cms.untracked.vstring("selectedPatJetsPF2PAT","selectedPatJetsAK5PF","selectedPatJetsKT4PF"),
		JPTJetProducer = cms.InputTag("selectedPatJetsAK5JPT"),
		vJPTJetProducer = cms.untracked.vstring("selectedPatJetsAK5JPT"),
		genJetProducer = cms.InputTag("ak5GenJets"),
		vgenJetProducer = cms.untracked.vstring("ak5GenJets","ak5GenJetsNoE"),
		muonProducer = cms.InputTag("selectedPatMuons"),
		electronProducer = cms.InputTag("cleanPatElectronsTriggerMatch"),
		CalometProducer = cms.InputTag("patMETs"),
		PFmetProducer = cms.InputTag("patMETsPF2PAT"),
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
