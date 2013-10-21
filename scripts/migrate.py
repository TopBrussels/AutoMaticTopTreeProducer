SRC_URL = 'http://cmsdbsprod.cern.ch/cms_dbs_prod_global/servlet/DBSServlet'
DST_URL = 'https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet'
DATASET = '/MinimumBias/Commissioning10-PromptReco-v9/RECO'

from DBSAPI.dbsApi import DbsApi
DbsApi().migrateDatasetContents(SRC_URL, DST_URL, DATASET)

