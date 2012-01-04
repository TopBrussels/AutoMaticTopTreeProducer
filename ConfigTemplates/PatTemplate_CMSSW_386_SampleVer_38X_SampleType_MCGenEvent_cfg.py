from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.patTemplate_cfg import *
## DISABLE Options and Output Report AND output for every event
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )
process.MessageLogger.cerr.FwkReport.reportEvery = 100
from PhysicsTools.PatAlgos.tools.cmsswVersionTools import *
from PhysicsTools.PatAlgos.tools.jetTools import *
from PhysicsTools.PatAlgos.tools.muonTools import addMuonUserIsolation
process.load("TopBrussels.TopTreeProducer.patDefaultWithEleTrig_cff")
process.load("TopBrussels.TopTreeProducer.genJetNoElectron_cfi")
cleanGenJetsName = "ak5GenJets"
try:
	if not process.ak5GenJetsNoE is None:
		print "-> Rebuilding standard ak5GenJets and renaming the cleaned ak5GenJets to ak5GenJetsNoE"
		process.load("RecoJets.Configuration.GenJetParticles_cff")
		process.load("RecoJets.JetProducers.ak5GenJets_cfi")
		process.makePatJets.replace( process.patJetCharge, process.genParticlesForJets+process.ak5GenJets+process.patJetCharge)
		cleanGenJetsName = "ak5GenJetsNoE"
except:
	print "-> Not rebuilding the standard collection, because the cleaned genjets are built with the same name"

process.load("TopBrussels.TopTreeProducer.TowerCleaningSequence_cff")
addMuonUserIsolation(process)
process.load("TopQuarkAnalysis.TopEventProducers.sequences.ttGenEvent_cff");

 # Adding TCMet 
from PhysicsTools.PatAlgos.tools.metTools import *
addTcMET(process,"TC")
 
# for 38X we need to modify the jes temporary
process.load('JetMETCorrections.Configuration.DefaultJEC_cff') 
process.ak5CaloL2Relative.useCondDB = False 
process.ak5CaloL3Absolute.useCondDB = False 
process.ak5CaloResidual.useCondDB = False 

 # Adding jet collections
addJetCollection(process,
    cms.InputTag('ak5CaloJets'),
   'AK5','Calo',
    doJTA=True,
    doBTagging=True,
    jetCorrLabel=('AK5','Calo'),
    doType1MET=False,
    genJetCollection=cms.InputTag("ak5GenJets"),
    doJetID=True,
    jetIdLabel="ak5"
    )
addJetCollection(process,
    cms.InputTag('ak5PFJets'),
   'AK5','PF',
    doJTA=False,
    doBTagging=True,
    jetCorrLabel=('AK5','PF'),
    doType1MET=False,
    genJetCollection=cms.InputTag("ak5GenJets"),
    doJetID=False,
    jetIdLabel="AK5PF"
    )
addJetCollection(process,
    cms.InputTag('kt4CaloJets'),
   'KT4','Calo',
    doJTA=True,
    doBTagging=True,
    jetCorrLabel=('KT4','Calo'),
    doType1MET=False,
    genJetCollection=cms.InputTag("kt4GenJets"),
    doJetID=True,
    jetIdLabel="kt4"
    )
addJetCollection(process,
    cms.InputTag('kt4PFJets'),
   'KT4','PF',
    doJTA=False,
    doBTagging=True,
    jetCorrLabel=('KT4','PF'),
    doType1MET=False,
    genJetCollection=cms.InputTag("kt4GenJets"),
    doJetID=False,
    jetIdLabel="KT4PF"
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
    jetIdLabel="ak5"
    )
addJetCollection(process,
    cms.InputTag('newAntikt5CaloJets'),
   'CleanedAK5','Calo',
    doJTA=False,
    doBTagging=True,
    jetCorrLabel=('AK5','Calo'),
    doType1MET=False,
    doL1Cleaning = False,
    doL1Counters = False,
    genJetCollection=cms.InputTag(cleanGenJetsName),
    doJetID=False,
    )
# Configure PAT to use PF2PAT instead of AOD sources
# this function will modify the PAT sequences. It is currently
# not possible to run PF2PAT+PAT and standart PAT at the same time
from PhysicsTools.PatAlgos.tools.pfTools import *
# An empty postfix means that only PF2PAT is run,  
# otherwise both standard PAT and PF2PAT are run. In the latter case PF2PAT
## collections have standard names + postfix (e.g. patElectronPFlow)
postfix = "PF2PAT"
usePF2PAT(process,runPF2PAT=True, jetAlgo='AK5', runOnMC=True, postfix=postfix)
getattr(process, "patElectrons"+postfix).embedGenMatch = True
getattr(process, "patMuons"+postfix).embedGenMatch = True
# We need to adapt some parameters of patMHT to make it work
process.patMHTs.jetTag       = cms.untracked.InputTag("patJets")
process.patMHTs.electronTag  = cms.untracked.InputTag("patElectrons")
process.patMHTs.muonTag      = cms.untracked.InputTag("patMuons")
process.patMHTs.tauTag       = cms.untracked.InputTag("patTaus")
process.patMHTs.photonTag    = cms.untracked.InputTag("patPhotons")

process.patJets.addTagInfos = cms.bool(False)

process.p = cms.Path(
cms.Sequence(
process.genJet *
process.makeGenEvt *
process.TowerCleaningSeq *
process.patCandidates *
process.makePatMHTs * # patMHTs are disabled by default in 38X
process.selectedPatCandidates *
process.cleanPatCandidates *
process.patAddTrigger ) +getattr(process,"patPF2PATSequence"+postfix)
 )
process.GlobalTag.globaltag = "START38_V13::All"
readFiles = cms.untracked.vstring()
secFiles = cms.untracked.vstring()
readFiles.extend( [
       'file:/user/mmaes/38XAODSIM_2.root' ] );
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
process.out.outputCommands.extend(cms.vstring("keep DcsStatuss_scalersRawToDigi__RECO"))
process.out.outputCommands.extend(cms.vstring("keep GenEventInfoProduct_*_*_*"))

process.out.fileName = "30112010_104727_PAT.root"
