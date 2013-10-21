# Starting with a skeleton process which gets imported with the following line
from PhysicsTools.PatAlgos.patTemplate_cfg import *

from PhysicsTools.PatAlgos.tools.coreTools import *

process.source.fileNames = [
#"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/EAEFC3A5-DB85-E011-BB31-0030487A17B8.root",
#"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/F6833FFE-7685-E011-9FB5-0030487C90C2.root",
#"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/12AE4A22-7085-E011-9BAB-001D09F2AD84.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/E0842679-7A85-E011-9904-0030487CD700.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/C89BAA53-6885-E011-9A66-00304879BAB2.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/4E271B3A-8285-E011-B14A-003048F1C424.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/221B5FF0-A185-E011-8FE6-001D09F25456.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/2854C5BA-2786-E011-91DC-001D09F231B0.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/F6F389DA-AD85-E011-94B9-0030487C7E18.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/A456D61A-CA85-E011-B4C2-003048D2BC42.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/121BDBF2-A185-E011-B033-001D09F27067.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/3C29A216-CA85-E011-8925-0030486780AC.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/B8D5FCCD-8085-E011-8943-003048F118DE.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/884E3465-A585-E011-A2FA-0030487A3232.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/804CCA40-B685-E011-8175-0030487CD7EE.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/58CB431B-CA85-E011-9D75-003048D2C0F2.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/0C7C839F-B585-E011-92C5-001D09F2426D.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/24FB6EA9-B585-E011-917A-0030487CD716.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/6AD306BB-C585-E011-8280-001D09F29597.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/8EDC7C0B-6E85-E011-8696-001D09F2447F.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/ECE703F0-BB85-E011-850F-0030487CD710.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/E479760A-6E85-E011-9FC9-001D09F29146.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/CA22ABA6-7785-E011-86C5-001D09F244BB.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/448370A3-C185-E011-8BE3-001D09F24303.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/C87C27D7-C785-E011-A1AF-0019B9F704D6.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/FA6A53AB-CA85-E011-85B3-003048D37514.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/E00F13A0-A985-E011-8EA4-001D09F291D2.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/DE2D7C23-7485-E011-8EA5-0030487C90EE.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/A8BD8F1F-A685-E011-BA48-001617E30CC2.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/AC5F4310-9D85-E011-AAE4-001D09F232B9.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/EA2A8265-A585-E011-865B-00304879FA4C.root",
"/store/data/Run2011A/HT/AOD/PromptReco-v4/000/165/415/28A107CB-AB85-E011-ADA4-0030487A3C92.root"
]

###############################
####### Global Setup ##########
###############################

process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.GlobalTag.globaltag = cms.string('GR_R_42_V13::All')

# require scraping filter
process.scrapingVeto = cms.EDFilter("FilterOutScraping",
                                    applyfilter = cms.untracked.bool(True),
                                    debugOn = cms.untracked.bool(False),
                                    numtrack = cms.untracked.uint32(10),
                                    thresh = cms.untracked.double(0.2)
                                    )

# HB + HE noise filtering
process.load('CommonTools/RecoAlgos/HBHENoiseFilter_cfi')
process.HBHENoiseFilter.minIsolatedNoiseSumE = cms.double(999999.) #added
process.HBHENoiseFilter.minNumIsolatedNoiseChannels = cms.int32(999999) #added
process.HBHENoiseFilter.minIsolatedNoiseSumEt = cms.double(999999.) #added

# switch on PAT trigger
#from PhysicsTools.PatAlgos.tools.trigTools import switchOnTrigger
#switchOnTrigger( process, '*' )


##-------------------- Import the Jet RECO modules -----------------------
process.load('RecoJets.Configuration.RecoPFJets_cff')
##-------------------- Turn-on the FastJet density calculation -----------------------
process.kt6PFJets.doRhoFastjet = True
##-------------------- Turn-on the FastJet jet area calculation for your favorite algorithm -----------------------
process.ak5PFJets.doAreaFastjet = True

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
####### PF2PAT Setup ##########
###############################

# Default PF2PAT with AK5 jets. Make sure to turn ON the L1fastjet stuff. 
from PhysicsTools.PatAlgos.tools.pfTools import *
postfix = "PF2PAT"
usePF2PAT(process,runPF2PAT=True, jetAlgo='AK5', runOnMC=False, postfix=postfix)
process.pfPileUpPF2PAT.Enable = True
#process.pfJetsPF2PAT.Vertices = cms.InputTag('goodOfflinePrimaryVertices') #commented pfJetsPF2PAT ParameterSet has no member Vertices
process.pfPileUpPF2PAT.Vertices = 'goodOfflinePrimaryVertices' #added
process.pfJetsPF2PAT.doAreaFastjet = True
process.pfJetsPF2PAT.doRhoFastjet = False
process.patJetCorrFactorsPF2PAT.payload = 'AK5PFchs'
process.patJetCorrFactorsPF2PAT.levels = cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute'])
process.patJetCorrFactorsPF2PAT.rho = cms.InputTag("kt6PFJetsPF2PAT", "rho")
process.pfPileUpPF2PAT.checkClosestZVertex = False

#process.muonMatchPF2PAT.src = "pfIsolatedMuonsPF2PAT"
#process.patElectronsPF2PAT.embedTrack = cms.bool(True)
#process.patMuonsPF2PAT.embedTrack = cms.bool(True)

# Use the good primary vertices everywhere. 
for imod in [process.patMuonsPF2PAT, process.patElectronsPF2PAT] :
    imod.pvSrc = "goodOfflinePrimaryVertices"
    imod.embedTrack = cms.bool(True)


###############################
### TagInfo and Matching Setup#
###############################

#process.patJetsPF2PAT.embedGenJetMatch = True
#process.patJetsPF2PAT.getJetMCFlavour = True
#process.patJetsPF2PAT.addGenPartonMatch = True
# Add the calo towers and PFCandidates.
process.patJetsPF2PAT.embedCaloTowers = True
process.patJetsPF2PAT.embedPFCandidates = True
process.patJetsPF2PAT.tagInfoSources = cms.VInputTag(
    cms.InputTag("secondaryVertexTagInfosAODPF2PAT")
    )

###############################
###### Bare KT 0.6 jets #######
###############################

from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
process.kt6PFJetsPF2PAT = kt4PFJets.clone(
    rParam = cms.double(0.6),
    src = cms.InputTag('pfNoElectronPF2PAT'),
    doAreaFastjet = cms.bool(True),
    doRhoFastjet = cms.bool(True),
    voronoiRfact = cms.double(0.9)
    )

getattr(process,"patPF2PATSequencePF2PAT").replace( getattr(process,"pfNoElectronPF2PAT"), getattr(process,"pfNoElectronPF2PAT")*getattr(process,"kt6PFJetsPF2PAT") )


# Remove MC Matching (needs to be before addJetCollection)
removeMCMatching( process, ['All'] )


# addJetCollection stuff		
from PhysicsTools.PatAlgos.tools.jetTools import *

addJetCollection(process,cms.InputTag('JetPlusTrackZSPCorJetAntiKt5'),
                 'AK5', 'JPT',
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5JPT', cms.vstring(['L1Offset', 'L2Relative', 'L3Absolute'])),
                 doType1MET   = False,
                 doL1Cleaning = False,
                 doL1Counters = False,                 
                 genJetCollection = cms.InputTag("ak5GenJets"),
                 doJetID      = True,
                 jetIdLabel   = "ak5"
                 )

addJetCollection(process,cms.InputTag('ak5CaloJets'),
                 'AK5', 'Calo',
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5Calo', cms.vstring(['L1Offset', 'L2Relative', 'L3Absolute'])),
                 doType1MET   = True,                            
                 doL1Cleaning = False,
                 doL1Counters = False,
                 genJetCollection=cms.InputTag("ak5GenJets"),
                 doJetID      = True,
                 jetIdLabel   = "ak5",
                 )

addJetCollection(process,cms.InputTag('ak5PFJets'),
                 'AK5', 'PF',
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5PF', cms.vstring(['L1Offset', 'L2Relative', 'L3Absolute'])),
                 doType1MET   = False,                            
                 doL1Cleaning = False,
                 doL1Counters = False,
                 genJetCollection=cms.InputTag("ak5GenJets"),
                 doJetID      = True,
                 jetIdLabel   = "ak5",
                 )


###############################
#### Selections Setup #########
###############################

# AK5 Jets
#   PF
process.selectedPatJetsPF2PAT.cut = cms.string("pt > 20")
process.selectedPatJetsAK5PF.cut = cms.string("pt > 20")
process.selectedPatJetsAK5JPT.cut = cms.string("pt > 20")
process.selectedPatJetsAK5Calo.cut = cms.string("pt > 20")


# Add tcMET
from PhysicsTools.PatAlgos.tools.metTools import *
addTcMET(process, 'TC')

#process.selectedPatJetsAK5PF.addGenPartonMatch = cms.bool(False)
#process.selectedPatJetsAK5PF.getJetMCFlavour = cms.bool(False)
#process.selectedPatJetsAK5PF.embedGenJetMatch = cms.bool(False)
#process.patJetsPF2PAT.embedGenJetMatch = True
#process.patJetsPF2PAT.getJetMCFlavour = True
#process.patJetsPF2PAT.addGenPartonMatch = True


# let it run

process.patseq = cms.Sequence(
		process.kt6PFJets*
		process.ak5PFJets*
    process.scrapingVeto*
    process.HBHENoiseFilter*
	  process.goodOfflinePrimaryVertices* 
    process.primaryVertexFilter * #removes events with no good pv (but if cuts to determine good pv change...)
    getattr(process,"patPF2PATSequence"+postfix)*
    process.patDefaultSequence
    )

process.p0 = cms.Path(
    process.patseq
    )

process.out.SelectEvents.SelectEvents = cms.vstring('p0')
    
# rename output file
process.out.fileName = cms.untracked.string('test_42_Data_PAT.root')


# reduce verbosity
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(100)


# process all the events
process.maxEvents.input = -1 #changed
process.options.wantSummary = False
process.out.dropMetaData = cms.untracked.string("DROPPED")

process.source.inputCommands = cms.untracked.vstring("keep *", "drop *_MEtoEDMConverter_*_*")

process.out.outputCommands = [
    'drop *_cleanPat*_*_*',
    'keep *_selectedPat*_*_*',
    'keep *_goodPat*_*_*',
    'keep patJets_selectedPat*_*_*',
    'keep *_patMETs*_*_*',
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
