from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.patTemplate_cfg import *
## DISABLE Options and Output Report AND output for every event
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )
process.MessageLogger.cerr.FwkReport.reportEvery = 100
from PhysicsTools.PatAlgos.tools.cmsswVersionTools import *
from PhysicsTools.PatAlgos.tools.jetTools import *
from PhysicsTools.PatAlgos.tools.muonTools import addMuonUserIsolation
from RecoEgamma.EgammaTools.correctedElectronsProducer_cfi import *
process.load("RecoEgamma.ElectronIdentification.electronIdSequence_cff")
process.load("CommonTools/RecoAlgos/HBHENoiseFilter_cfi")
process.load("TopBrussels.TopTreeProducer.patDefaultWithEleTrig_cff")
process.gsfElectrons = gsfElectrons
process.patElectrons.electronSource = "gsfElectrons::PAT"
process.load("TopBrussels.TopTreeProducer.patDefaultWithEleTrig_cff")
addMuonUserIsolation(process)
removeMCMatching(process, ['All'])

 # Adding TCMet 
from PhysicsTools.PatAlgos.tools.metTools import *
addTcMET(process,"TC")
 

 # Adding jet collections
addJetID(process, cms.InputTag('ak5CaloJets'), 'AK5')
addJetCollection(process,
    cms.InputTag('ak5CaloJets'),
   'AK5','Calo',
    doJTA=True,
    doBTagging=True,
    jetCorrLabel=('AK5','Calo'),
    doType1MET=False,
    genJetCollection=cms.InputTag("ak5GenJets"),
    doJetID=True,
    jetIdLabel="AK5"
    )
addJetID(process, cms.InputTag('iterativeCone5CaloJets'), 'IC5')
addJetCollection(process,
    cms.InputTag('iterativeCone5CaloJets'),
   'IC5','Calo',
    doJTA=True,
    doBTagging=True,
    jetCorrLabel=('IC5','Calo'),
    doType1MET=False,
    genJetCollection=cms.InputTag("iterativeCone5GenJets"),
    doJetID=True,
    jetIdLabel="IC5"
    )
addJetID(process, cms.InputTag('kt4CaloJets'), 'KT4')
addJetCollection(process,
    cms.InputTag('kt4CaloJets'),
   'KT4','Calo',
    doJTA=True,
    doBTagging=True,
    jetCorrLabel=('KT4','Calo'),
    doType1MET=False,
    genJetCollection=cms.InputTag("kt4GenJets"),
    doJetID=True,
    jetIdLabel="KT4"
    )
addJetCollection(process,
    cms.InputTag('JetPlusTrackZSPCorJetAntiKt5'),
   'AK5','JPT',
    doJTA=True,
    doBTagging=True,
    jetCorrLabel=('AK5','JPT'),
    doType1MET=False,
    genJetCollection=cms.InputTag("ak5GenJets"),
    doJetID=True,
    jetIdLabel="AK5"
    )
process.AK5JetID = cms.EDProducer("JetIDProducer",
	eeRecHitsColl = cms.InputTag("ecalRecHit","EcalRecHitsEE"),
	hbheRecHitsColl = cms.InputTag("hbhereco"),
	hoRecHitsColl = cms.InputTag("horeco"),
	ebRecHitsColl = cms.InputTag("ecalRecHit","EcalRecHitsEB"),
	hfRecHitsColl = cms.InputTag("hfreco"),
	rpcRecHits = cms.InputTag("rpcRecHits"),
	useRecHits = cms.bool(True),
	src = cms.InputTag("ak5CaloJets")
)
process.IC5JetID = cms.EDProducer("JetIDProducer",
	eeRecHitsColl = cms.InputTag("ecalRecHit","EcalRecHitsEE"),
	hbheRecHitsColl = cms.InputTag("hbhereco"),
	hoRecHitsColl = cms.InputTag("horeco"),
	ebRecHitsColl = cms.InputTag("ecalRecHit","EcalRecHitsEB"),
	hfRecHitsColl = cms.InputTag("hfreco"),
	rpcRecHits = cms.InputTag("rpcRecHits"),
	useRecHits = cms.bool(True),
	src = cms.InputTag("iterativeCone5CaloJets")
)
process.KT4JetID = cms.EDProducer("JetIDProducer",
	eeRecHitsColl = cms.InputTag("ecalRecHit","EcalRecHitsEE"),
	hbheRecHitsColl = cms.InputTag("hbhereco"),
	hoRecHitsColl = cms.InputTag("horeco"),
	ebRecHitsColl = cms.InputTag("ecalRecHit","EcalRecHitsEB"),
	hfRecHitsColl = cms.InputTag("hfreco"),
	rpcRecHits = cms.InputTag("rpcRecHits"),
	useRecHits = cms.bool(True),
	src = cms.InputTag("kt4CaloJets")
)
# We need to add some VBTF eleID for the refsel
process.load("TopBrussels.TopTreeProducer.simpleEleIdSequence_cff")
process.patElectronIDs = cms.Sequence(process.simpleEleIdSequence)
process.patElectrons.addElectronID = cms.bool(True)
process.patElectrons.electronIDSources = cms.PSet(
	simpleEleId60cIso= cms.InputTag("simpleEleId70cIso"),
	simpleEleId70cIso= cms.InputTag("simpleEleId60cIso"),
	simpleEleId80cIso= cms.InputTag("simpleEleId80cIso"),
	simpleEleId85cIso= cms.InputTag("simpleEleId85cIso"),
	simpleEleId90cIso= cms.InputTag("simpleEleId90cIso"),
	simpleEleId95cIso= cms.InputTag("simpleEleId95cIso"),
	simpleEleId60relIso= cms.InputTag("simpleEleId70relIso"),
	simpleEleId70relIso= cms.InputTag("simpleEleId60relIso"),
	simpleEleId80relIso= cms.InputTag("simpleEleId80relIso"),
	simpleEleId85relIso= cms.InputTag("simpleEleId85relIso"),
	simpleEleId90relIso= cms.InputTag("simpleEleId90relIso"),
	simpleEleId95relIso= cms.InputTag("simpleEleId95relIso"),
	eidRobustLoose = cms.InputTag("eidRobustLoose"),
	eidRobustTight = cms.InputTag("eidRobustTight"),
	eidRobustHighEnergy = cms.InputTag("eidRobustHighEnergy"),
	eidLoose = cms.InputTag("eidLoose"),
	eidTight = cms.InputTag("eidTight"),
)
# We need to adapt some parameters of patMHT to make it work in 38X
process.patMHTs.jetTag       = cms.untracked.InputTag("patJets")
process.patMHTs.electronTag  = cms.untracked.InputTag("patElectrons")
process.patMHTs.muonTag      = cms.untracked.InputTag("patMuons")
process.patMHTs.tauTag       = cms.untracked.InputTag("patTaus")
process.patMHTs.photonTag    = cms.untracked.InputTag("patPhotons")

# Configure PAT to use PF2PAT instead of AOD sources
# this function will modify the PAT sequences. It is currently
# not possible to run PF2PAT+PAT and standart PAT at the same time
from PhysicsTools.PatAlgos.tools.pfTools import *
# An empty postfix means that only PF2PAT is run,  
# otherwise both standard PAT and PF2PAT are run. In the latter case PF2PAT
## collections have standard names + postfix (e.g. patElectronPFlow)
postfix = "PF"
usePF2PAT(process,runPF2PAT=True, jetAlgo='AK5', runOnMC=False, postfix=postfix)
getattr(process, "patElectrons"+postfix).embedGenMatch = False
getattr(process, "patMuons"+postfix).embedGenMatch = False
process.p = cms.Path(process.HBHENoiseFilter *
cms.Sequence(
 process.gsfElectrons * process.eIdSequence * process.patElectronIDs * 
process.AK5JetID * process.IC5JetID * process.KT4JetID * 
process.patCandidates *
process.makePatMHTs * # patMHTs are disabled by default in 38X
process.selectedPatCandidates *
process.cleanPatCandidates *
process.patAddTrigger ) +getattr(process,"patPF2PATSequence"+postfix)
 )
process.GlobalTag.globaltag = "GR_R_38X_V13::All"
readFiles = cms.untracked.vstring()
secFiles = cms.untracked.vstring()
readFiles.extend( [
       'file:/user/mmaes/38Xpreprod.root' ] );
process.source.fileNames = readFiles
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
process.out.outputCommands.extend(cms.vstring("keep recoGenJets_ak5GenJets*_*_PAT"))
process.out.outputCommands.extend(cms.vstring("keep TtGenEvent_*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop *_*CaloPF_*_*"))
process.out.outputCommands.extend(cms.vstring("drop *_*JPTPF_*_*"))
process.out.outputCommands.extend(cms.vstring("drop patPhotons_*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop patTaus_*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop patMHTs_*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop patMETs_*_*_*"))
process.out.outputCommands.extend(cms.vstring("drop patJets_selectedPatJets__PAT"))
process.out.outputCommands.extend(cms.vstring("drop *_cleanPat*_*_*"))
process.out.outputCommands.extend(cms.vstring("keep patMETs_patMETs*__PAT"))
process.out.outputCommands.extend(cms.vstring("keep patMHTs_patMHTs__PAT"))
process.out.outputCommands.extend(cms.vstring("keep *_cleanPatElectronsTriggerMatch_*_*"))
process.out.outputCommands.extend(cms.vstring("keep *_*_EcalRecHitsEB_*"))
process.out.outputCommands.extend(cms.vstring("keep GenEventInfoProduct_*_*_*"))

process.out.fileName = "06102010_120616_PAT.root"
