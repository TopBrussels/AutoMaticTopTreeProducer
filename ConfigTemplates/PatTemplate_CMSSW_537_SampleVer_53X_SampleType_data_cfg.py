# Starting with a skeleton process which gets imported with the following line
from PhysicsTools.PatAlgos.patTemplate_cfg import *

from PhysicsTools.PatAlgos.tools.coreTools import *

process.source.fileNames = [
#"file:Data_53X_AOD.root"
#'/store/data/Run2012B/SingleMu/AOD/TOPMuPlusJets-PromptSkim-v2/000/196/197/0000/AEFD9DB5-2BBA-E111-B471-E0CB4E19F98A.root' #52X file!!
'file:SingleMu_53X_Run2012DPRv1_AOD_5E4544F8-7E0D-E211-A668-001D09F2441B.root'
]

## import skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *

# load the PAT config
process.load("PhysicsTools.PatAlgos.patSequences_cff")

###############################
####### Global Setup ##########
###############################

process.load("FWCore.Framework.test.cmsExceptionsFatal_cff")
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

process.GlobalTag.globaltag = cms.string('FT_53_V21_AN3::All')

##############################################
#### Apply latest J(B)P B-tag calibration ####
##############################################

#process.GlobalTag.toGet = cms.VPSet(
#  cms.PSet(record = cms.string("BTagTrackProbability2DRcd"),
#       tag = cms.string("TrackProbabilityCalibration_2D_Data53X_v2"),
#       connect = cms.untracked.string("frontier://FrontierPrep/CMS_COND_BTAU")),
#  cms.PSet(record = cms.string("BTagTrackProbability3DRcd"),
#       tag = cms.string("TrackProbabilityCalibration_3D_Data53X_v2"),
#       connect = cms.untracked.string("frontier://FrontierPrep/CMS_COND_BTAU"))
#)

##############################################
#### Add new retrained CSV b tagging algo ####
##############################################

process.load("CondCore.DBCommon.CondDBSetup_cfi")

process.BTauMVAJetTagComputerRecord = cms.ESSource("PoolDBESSource",
	process.CondDBSetup,
	timetype = cms.string('runnumber'),
	toGet = cms.VPSet(cms.PSet(
		record = cms.string('BTauGenericMVAJetTagComputerRcd'),
                tag = cms.string('MVAComputerContainer_Retrained53X_JetTags_v2')
	)),
	connect = cms.string('frontier://FrontierProd/CMS_COND_PAT_000'),
	BlobStreamerName = cms.untracked.string('TBufferBlobStreamingService')
)

process.es_prefer_BTauMVAJetTagComputerRecord = cms.ESPrefer("PoolDBESSource","BTauMVAJetTagComputerRecord")

process.load("RecoBTag.SecondaryVertex.combinedSecondaryVertexES_cfi")
process.load("RecoBTag.SecondaryVertex.combinedSecondaryVertexBJetTags_cfi")

process.combinedSecondaryVertexRetrained = process.combinedSecondaryVertex.clone()
process.combinedSecondaryVertexRetrained.calibrationRecords = cms.vstring(
      'CombinedSVRetrainRecoVertex', 
      'CombinedSVRetrainPseudoVertex', 
      'CombinedSVRetrainNoVertex'
      )

process.combinedSecondaryVertexRetrainedBJetTags = process.combinedSecondaryVertexBJetTags.clone()
process.combinedSecondaryVertexRetrainedBJetTags.jetTagComputer = cms.string('combinedSecondaryVertexRetrained')

from RecoBTag.Configuration.RecoBTag_cff import *

# for new softElectron tagger
from RecoBTag.SoftLepton.softLepton_cff import *
process.load("RecoBTag.SoftLepton.softLepton_cff")
process.softPFElectronRetrained = process.softElectron.clone()
# for new softMuon tagger
process.softPFMuonRetrained = process.softMuon.clone()


# for new supertaggers 
from RecoBTau.JetTagComputer.combinedMVA_cff import *
process.load("RecoBTau.JetTagComputer.combinedMVA_cff")

# for new supertaggers 
# CSV + JP
process.combinedCSVJP = process.combinedMVA.clone(
	calibrationRecord = 'CombinedCSVJP',
	jetTagComputers = cms.VPSet(
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('jetProbability')
                ),
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('combinedSecondaryVertexRetrained')
                ),
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('softPFMuonRetrained')
                ),
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('softPFElectronRetrained')
                )
        )
)
process.combinedCSVJPBJetTags = process.combinedMVABJetTags.clone(
	jetTagComputer = 'combinedCSVJP',
	tagInfos = cms.VInputTag(
                cms.InputTag("impactParameterTagInfos"),
                cms.InputTag("secondaryVertexTagInfos"),
								cms.InputTag("softPFMuonsTagInfos"),
                cms.InputTag("softPFElectronsTagInfos")
        )
)

# CSV + JP + SL
process.combinedCSVJPSL = process.combinedMVA.clone(
	calibrationRecord = 'CombinedCSVJPSL',
	jetTagComputers = cms.VPSet(
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('jetProbability')
                ),
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('combinedSecondaryVertexRetrained')
                ),
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('softPFMuonRetrained')
                ),
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('softPFElectronRetrained')
                )
        )
)
process.combinedCSVJPSLBJetTags = process.combinedMVABJetTags.clone(
	jetTagComputer = 'combinedCSVJPSL',
	tagInfos = cms.VInputTag(
                cms.InputTag("impactParameterTagInfos"),
                cms.InputTag("secondaryVertexTagInfos"),
								cms.InputTag("softPFMuonsTagInfos"),
                cms.InputTag("softPFElectronsTagInfos")
        )
)

# CSV + SL
process.combinedCSVSL = process.combinedMVA.clone(
	calibrationRecord = 'CombinedCSVSL',
	jetTagComputers = cms.VPSet(
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('jetProbability')
                ),
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('combinedSecondaryVertexRetrained')
                ),
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('softPFMuonRetrained')
                ),
                cms.PSet(
                        discriminator = cms.bool(True),
                        variables = cms.bool(False),
                        jetTagComputer = cms.string('softPFElectronRetrained')
                )
        )
)
process.combinedCSVSLBJetTags = process.combinedMVABJetTags.clone(
	jetTagComputer = 'combinedCSVSL',
	tagInfos = cms.VInputTag(
                cms.InputTag("impactParameterTagInfos"),
                cms.InputTag("secondaryVertexTagInfos"),
		cms.InputTag("softPFMuonsTagInfos"),
                cms.InputTag("softPFElectronsTagInfos")
        )
)


######################
#### Data filters ####
######################

# require scraping filter
process.scrapingVeto = cms.EDFilter("FilterOutScraping",
                                    applyfilter = cms.untracked.bool(True),
                                    debugOn = cms.untracked.bool(False),
                                    numtrack = cms.untracked.uint32(10),
                                    thresh = cms.untracked.double(0.25)
                                    )

# CSC Beam Halo Filter
process.load('RecoMET.METAnalyzers.CSCHaloFilter_cfi')

# HB + HE noise filter
process.load('CommonTools/RecoAlgos/HBHENoiseFilter_cfi')

# HCAL laser events filter
#process.load("RecoMET.METFilters.hcalLaserEventFilter_cfi")
#process.hcalLaserEventFilter.vetoByRunEventNumber=cms.untracked.bool(False)
#process.hcalLaserEventFilter.vetoByHBHEOccupancy=cms.untracked.bool(True)
#process.load("EventFilter.HcalRawToDigi.hcallasereventfilter2012_cfi")

# ECAL dead cell filter
process.load('RecoMET.METFilters.EcalDeadCellTriggerPrimitiveFilter_cfi')

# Tracking failure filter
process.load('RecoMET.METFilters.trackingFailureFilter_cfi')
process.trackingFailureFilter.VertexSource = cms.InputTag("goodOfflinePrimaryVertices", "", "")

### The tracking POG filters
process.load('RecoMET.METFilters.trackingPOGFilters_cff')

# The EE bad SuperCrystal filter
process.load('RecoMET.METFilters.eeBadScFilter_cfi')

# EB or EE Xtals with large laser calibration correction (added) 
process.load('RecoMET.METFilters.ecalLaserCorrFilter_cfi') 

##-------------------- Import the Jet RECO modules ----------------------- ## this makes cmsRun crash
##
process.load('RecoJets.Configuration.RecoPFJets_cff')
##-------------------- Turn-on the FastJet density calculation -----------------------
process.kt6PFJets.doRhoFastjet = True

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
#### Load MVA electron Id #####
###############################

process.load('EGamma.EGammaAnalysisTools.electronIdMVAProducer_cfi')
process.eidMVASequence = cms.Sequence( process.mvaTrigV0 + process.mvaNonTrigV0 )
                
###############################
####### PF2PAT Setup ##########
###############################

# Default PF2PAT with AK5 jets. Make sure to turn ON the L1fastjet stuff. 
from PhysicsTools.PatAlgos.tools.pfTools import *
postfix = "PF2PAT"
usePF2PAT(process,runPF2PAT=True, jetAlgo="AK5", runOnMC=False, postfix=postfix, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'), typeIMetCorrections=True)

process.patJetsPF2PAT.addTagInfos = cms.bool(True) 

process.patJetsPF2PAT.tagInfoSources = cms.VInputTag(
        cms.InputTag("impactParameterTagInfosAODPF2PAT"),
	cms.InputTag("secondaryVertexTagInfosAODPF2PAT"),
	cms.InputTag("softMuonTagInfosAODPF2PAT"),
	cms.InputTag("softElectronTagInfosAODPF2PAT"),
	cms.InputTag("secondaryVertexNegativeTagInfosAODPF2PAT"),
	cms.InputTag("inclusiveSecondaryVertexFinderTagInfosAODPF2PAT"),
	cms.InputTag("softPFMuonsTagInfosAODPF2PAT"),
	cms.InputTag("softPFElectronsTagInfosAODPF2PAT")
    )
    
process.patJetsPF2PAT.discriminatorSources = cms.VInputTag(
        cms.InputTag("combinedSecondaryVertexBJetTagsAODPF2PAT"),
        cms.InputTag("combinedSecondaryVertexRetrainedBJetTagsAODPF2PAT"),
        cms.InputTag("combinedSecondaryVertexMVABJetTagsAODPF2PAT"),
        cms.InputTag("jetBProbabilityBJetTagsAODPF2PAT"),
        cms.InputTag("jetProbabilityBJetTagsAODPF2PAT"),
        cms.InputTag("simpleSecondaryVertexHighEffBJetTagsAODPF2PAT"),
        cms.InputTag("simpleSecondaryVertexHighPurBJetTagsAODPF2PAT"),
        cms.InputTag("softElectronByPtBJetTagsAODPF2PAT"),
        cms.InputTag("softElectronByIP3dBJetTagsAODPF2PAT"),
        cms.InputTag("softMuonBJetTagsAODPF2PAT"),
        cms.InputTag("softMuonByPtBJetTagsAODPF2PAT"),
        cms.InputTag("softMuonByIP3dBJetTagsAODPF2PAT"),
        cms.InputTag("trackCountingHighEffBJetTagsAODPF2PAT"),
        cms.InputTag("trackCountingHighPurBJetTagsAODPF2PAT"),
	cms.InputTag("combinedCSVJPBJetTagsAODPF2PAT"),
	cms.InputTag("combinedCSVJPSLBJetTagsAODPF2PAT"),
	cms.InputTag("combinedCSVSLBJetTagsAODPF2PAT"),
	cms.InputTag("softPFMuonBJetTagsAODPF2PAT"),
	cms.InputTag("softPFElectronBJetTagsAODPF2PAT"),
    )    

process.softElectronByPtBJetTagsAODPF2PAT = process.softMuonByIP3dBJetTagsAODPF2PAT.clone(
	jetTagComputer = 'softLeptonByPt',
	tagInfos = cms.VInputTag( cms.InputTag("softElectronTagInfosAODPF2PAT") )
	)
process.softElectronByIP3dBJetTagsAODPF2PAT = process.softMuonByIP3dBJetTagsAODPF2PAT.clone(
	jetTagComputer = 'softLeptonByIP3d',
	tagInfos = cms.VInputTag( cms.InputTag("softElectronTagInfosAODPF2PAT") )
	)
process.combinedSecondaryVertexRetrainedBJetTagsAODPF2PAT = process.combinedSecondaryVertexBJetTagsAODPF2PAT.clone(
   	jetTagComputer = 'combinedSecondaryVertexRetrained',
        )
process.combinedCSVJPBJetTagsAODPF2PAT = process.combinedMVABJetTagsAODPF2PAT.clone(
   	jetTagComputer = 'combinedCSVJP',
	tagInfos = cms.VInputTag(
                cms.InputTag("impactParameterTagInfosAODPF2PAT"),
                cms.InputTag("secondaryVertexTagInfosAODPF2PAT"),
		cms.InputTag("softPFMuonsTagInfosAODPF2PAT"),
                cms.InputTag("softPFElectronsTagInfosAODPF2PAT")
     )
        )
process.combinedCSVJPSLBJetTagsAODPF2PAT = process.combinedMVABJetTagsAODPF2PAT.clone(
   	jetTagComputer = 'combinedCSVJPSL',
        tagInfos = cms.VInputTag(
                cms.InputTag("impactParameterTagInfosAODPF2PAT"),
                cms.InputTag("secondaryVertexTagInfosAODPF2PAT"),
		cms.InputTag("softPFMuonsTagInfosAODPF2PAT"),
                cms.InputTag("softPFElectronsTagInfosAODPF2PAT")

     )   
				)
process.combinedCSVSLBJetTagsAODPF2PAT = process.combinedMVABJetTagsAODPF2PAT.clone(
   	jetTagComputer = 'combinedCSVSL',
	tagInfos = cms.VInputTag(
                cms.InputTag("impactParameterTagInfosAODPF2PAT"),
                cms.InputTag("secondaryVertexTagInfosAODPF2PAT"),
                cms.InputTag("softPFMuonsTagInfosAODPF2PAT"),
                cms.InputTag("softPFElectronsTagInfosAODPF2PAT") 
     )   
        )

process.softPFMuonsTagInfosAODPF2PAT.primaryVertex =  cms.InputTag("goodOfflinePrimaryVertices")
process.softPFElectronsTagInfosAODPF2PAT.primaryVertex =  cms.InputTag("goodOfflinePrimaryVertices")

process.softPFMuonBJetTagsAODPF2PAT.jetTagComputer = 	'softPFMuonRetrained'	
process.softPFElectronBJetTagsAODPF2PAT.jetTagComputer = 	'softPFElectronRetrained'			
	
#process.btaggingTagInfosAODPF2PAT.replace(process.softMuonTagInfosAODPF2PAT, process.softMuonTagInfosAODPF2PAT+process.softPFMuonsTagInfosAODPF2PAT+process.softPFElectronsTagInfosAODPF2PAT)
#process.btaggingJetTagsAODPF2PAT.replace(process.softMuonByIP3dBJetTagsAODPF2PAT, process.softMuonByIP3dBJetTagsAODPF2PAT+process.softElectronByPtBJetTagsAODPF2PAT+process.softElectronByIP3dBJetTagsAODPF2PAT+process.softPFElectronRetrainedBJetTagsAODPF2PAT+process.softPFMuonRetrainedBJetTagsAODPF2PAT)
process.btaggingJetTagsAODPF2PAT.replace(process.softMuonByIP3dBJetTagsAODPF2PAT, process.softMuonByIP3dBJetTagsAODPF2PAT+process.softElectronByPtBJetTagsAODPF2PAT+process.softElectronByIP3dBJetTagsAODPF2PAT)
process.btaggingJetTagsAODPF2PAT.replace(process.combinedSecondaryVertexBJetTagsAODPF2PAT,process.combinedSecondaryVertexBJetTagsAODPF2PAT+process.combinedSecondaryVertexRetrainedBJetTagsAODPF2PAT)
process.btaggingJetTagsAODPF2PAT.replace(process.combinedMVABJetTagsAODPF2PAT,process.combinedCSVJPBJetTagsAODPF2PAT+process.combinedCSVJPSLBJetTagsAODPF2PAT+process.combinedCSVSLBJetTagsAODPF2PAT)


process.pfIsolatedMuonsPF2PAT.isolationCut = cms.double(0.2)
process.pfIsolatedMuonsPF2PAT.doDeltaBetaCorrection = True
process.pfSelectedMuonsPF2PAT.cut = cms.string('pt > 10. && abs(eta) < 2.5')
process.pfIsolatedMuonsPF2PAT.isolationValueMapsCharged = cms.VInputTag(cms.InputTag("muPFIsoValueCharged04PF2PAT"))
process.pfIsolatedMuonsPF2PAT.deltaBetaIsolationValueMap = cms.InputTag("muPFIsoValuePU04PF2PAT")
process.pfIsolatedMuonsPF2PAT.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("muPFIsoValueNeutral04PF2PAT"), cms.InputTag("muPFIsoValueGamma04PF2PAT"))

print "process.pfIsolatedMuonsPF2PAT.isolationCut -> "+str(process.pfIsolatedMuonsPF2PAT.isolationCut)

# to use GsfElectrons instead of PF electrons
# this will destory the feature of top projection which solves the ambiguity between leptons and jets because
# there will be overlap between non-PF electrons and jets even though top projection is ON!
useGsfElectrons(process,postfix,"03") # to change isolation cone size to 0.3 as it is recommended by EGM POG, use "04" for cone size 0.4

#process.pfIsolatedElectronsPF2PAT.isolationCut = cms.double(0.2)
#process.pfIsolatedElectronsPF2PAT.doDeltaBetaCorrection = False
#process.pfSelectedElectronsPF2PAT.cut = cms.string('pt > 10. && abs(eta) < 2.5 && gsfTrackRef.isNonnull && gsfTrackRef.trackerExpectedHitsInner.numberOfLostHits<2')
#process.pfIsolatedElectronsPF2PAT.isolationValueMapsCharged = cms.VInputTag(cms.InputTag("elPFIsoValueCharged03PFIdPF2PAT"))
#process.pfIsolatedElectronsPF2PAT.deltaBetaIsolationValueMap = cms.InputTag("elPFIsoValuePU03PFIdPF2PAT")
#process.pfIsolatedElectronsPF2PAT.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("elPFIsoValueNeutral03PFIdPF2PAT"), cms.InputTag("elPFIsoValueGamma03PFIdPF2PAT"))

#process.patElectronsPF2PAT.isolationValues = cms.PSet(
#        pfChargedHadrons = cms.InputTag("elPFIsoValueCharged03PFIdPF2PAT"),
#        pfChargedAll = cms.InputTag("elPFIsoValueChargedAll03PFIdPF2PAT"),
#        pfPUChargedHadrons = cms.InputTag("elPFIsoValuePU03PFIdPF2PAT"),
#        pfNeutralHadrons = cms.InputTag("elPFIsoValueNeutral03PFIdPF2PAT"),
#        pfPhotons = cms.InputTag("elPFIsoValueGamma03PFIdPF2PAT")
#        )

process.patElectronsPF2PAT.electronIDSources.mvaTrigV0    = cms.InputTag("mvaTrigV0")
process.patElectronsPF2PAT.electronIDSources.mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0") 
process.patPF2PATSequencePF2PAT.replace( process.patElectronsPF2PAT, process.eidMVASequence * process.patElectronsPF2PAT )

process.patJetCorrFactorsPF2PAT.payload = 'AK5PFchs'
process.patJetCorrFactorsPF2PAT.levels = cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute','L2L3Residual'])
process.pfPileUpPF2PAT.checkClosestZVertex = False

# top projections in PF2PAT:
getattr(process,"pfNoPileUp"+postfix).enable = True
getattr(process,"pfNoMuon"+postfix).enable = True
getattr(process,"pfNoElectron"+postfix).enable = True
getattr(process,"pfNoTau"+postfix).enable = False
getattr(process,"pfNoJet"+postfix).enable = False

#####################################################################################################
#### Clone the PF2PAT sequence for data-driven QCD estimate, and for Stijn's JetMET service work ####
#####################################################################################################

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
######## MC Matching ##########
###############################

# Remove MC Matching (needs to be before addJetCollection)
removeMCMatching( process, ['All'] )

###############################
#### Selections Setup #########
###############################

# AK5 Jets
#   PF
process.selectedPatJetsPF2PAT.cut = cms.string("pt > 10")
process.selectedPatJetsPF2PATNoLeptonCleaning.cut = cms.string("pt > 10")

# let it run
process.patseq = cms.Sequence(
		process.CSCTightHaloFilter*
           	process.HBHENoiseFilter*
           	process.scrapingVeto*
            	#process.hcalLaserEventFilter*
		#process.hcallasereventfilter2012 *
            	process.EcalDeadCellTriggerPrimitiveFilter*
                process.goodOfflinePrimaryVertices* 
                process.primaryVertexFilter * #removes events with no good pv (but if cuts to determine good pv change...)
            	process.trackingFailureFilter*
            	process.eeBadScFilter*
                process.ecalLaserCorrFilter*
                process.trkPOGFilters*
#               process.kt6PFJetsForIsolation*
                getattr(process,"patPF2PATSequence"+postfix)* # main PF2PAT
                getattr(process,"patPF2PATSequence"+postfix+postfixNoLeptonCleaning) # PF2PAT FOR DATA_DRIVEN QCD
#               getattr(process,"patPF2PATSequence"+postfix+postfixNoPFnoPU)* # PF2PAT FOR JETS WITHOUT PFnoPU
#               process.patDefaultSequence
                )

#################
#### ENDPATH ####
#################

process.p = cms.Path(
        process.patseq
    )

process.out.SelectEvents.SelectEvents = cms.vstring('p')
    
# rename output file
process.out.fileName = "PAT_test_537_data.root"

# process all the events
process.maxEvents.input = 100 #changed
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
    'keep double_kt6PFJets_rho_*',
#   'keep double_kt6PFJetsForIsolation_rho_*',
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
    'drop *_patMETs_*_*',
#   'keep *_patMETs_*_*',
    'drop *_selectedPatJets_*_*',
    'drop *_selectedPatPhotons*_*_*'
    ]
