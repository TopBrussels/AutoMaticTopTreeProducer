# Class to handle SQL

#Note: there are python mysql classes available but this class is a wrapper around the linux mysql program.
#      This limits the deployability of the script (but we only run on m* so no problem), yet it makes it easyer to use  because #      we only want to write to the db (good!)

# interacting with the os
from subprocess import Popen, PIPE, STDOUT
import sys
import os, os.path

# time
import time, datetime

class SQLHandler:

    def __init__(self,dbName,dbUser,dbPass,dbHostName):

        self.dbUser=dbUser
        self.dbPass=dbPass
        self.dbName=dbName

        self.mysqlCmd="mysql"

        if not dbHostName == "":

            self.mysqlCmd += " -h "+dbHostName


    def execQuery(self):

        out = ""
        if os.path.exists("./query.sql"):
            
            cmd = self.mysqlCmd+' -u '+self.dbUser+' --password=\"'+self.dbPass+'\" < query.sql'
            pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            out = pExe.stdout.read()

            #print cmd

            try:

                os.remove("./query.sql")

            except:

                pass
            
        return out
    
    # create query works for select and insert statements. In case of SELECT, values is a string like "DataSet REGEXP someString". In the case of insert, values is an array of arrays which contain 2 elements: fieldname and value
    def createQuery(self,operation,table,fields,values):

        query = operation

        if not operation.rfind("SELECT") == -1:

            query += " "+fields+" FROM `"+table+"`"

            if not values == "":

                query += " WHERE "+str(values)

        elif not operation.rfind("DELETE") == -1:

            if not values == "":

                query += " FROM `"+table+"` WHERE "+str(values)

        elif not operation.rfind("UPDATE") == -1:

            if not values == "":

                query += " `"+table+"` "+str(values)

        elif not operation.rfind("INSERT") == -1:

            if len(values) > 0:

                # print fieldnames in insert query
                query += " `"+table+"` ("

                for i in range(0,len(values)):

                    if len(values[i]) == 2:

                        query += "`"+values[i][0]+"`"
                        
                        if not i == len(values)-1:

                            query += ", "

                # print values in insert query
                query += ") VALUES ("

                for i in range(0,len(values)):

                    if len(values[i]) == 2:

                        query += "'"+values[i][1]+"'"
                        
                        if not i == len(values)-1:

                            query += ", "

                query += ")"
       
        #print query

        f = open("query.sql","w")

        f.write("USE "+self.dbName+";\n"+query+";\n")

        f.close()

        return query
                
class topDBInterface:

    def __init__(self):

        # get the sensitive information from config file

        login=""
        password=""
        dbaseName=""
        dbaseHost=""
        
        for line in open(".config","r"):
            if not line.rfind("DBUser") == -1:
                login = line.split(" ")[1].split("\n")[0]
            elif not line.rfind("DBPass") == -1:
                password = line.split(" ")[1].split("\n")[0]
            elif not line.rfind("DBHost") == -1:
                dbaseHost = line.split(" ")[1].split("\n")[0]
            elif not line.rfind("DBName") == -1:
                dbaseName = line.split(" ")[1].split("\n")[0]
                
        self.sql = SQLHandler(dbaseName,login,password,dbaseHost)
            
    def insertPatTuple(self,user,inputDataSet,PublishName,PatVersion,CMSSWversion,StoragePath,CffPath,nEventsDBS,nEventsGRID,jobEff,EventContent,JSONCrab,RunSelection):

        values = []
        values.append([])
        values[len(values)-1].append("Date")
        values[len(values)-1].append(datetime.date.today().strftime("%Y-%m-%d"))
        values.append([])
        values[len(values)-1].append("User")
        values[len(values)-1].append(user)
        values.append([])
        values[len(values)-1].append("dataset_id")
        values[len(values)-1].append(self.datasetID(inputDataSet))
        values.append([])
        values[len(values)-1].append("name")
        values[len(values)-1].append(PublishName)
        values.append([])
        values[len(values)-1].append("PATVersion")
        values[len(values)-1].append(PatVersion)
        values.append([])
        values[len(values)-1].append("CMSSWversion")
        values[len(values)-1].append(CMSSWversion)
        values.append([])
        values[len(values)-1].append("TQAFversion")
        values[len(values)-1].append("NO TQAF")
        values.append([])
        values[len(values)-1].append("NofEventDBS")
        values[len(values)-1].append(str(nEventsDBS))
        values.append([])
        values[len(values)-1].append("NofEventAfterGrid")
        values[len(values)-1].append(str(nEventsGRID))
        values.append([])
        values[len(values)-1].append("JobEff")
        values[len(values)-1].append(str(jobEff))
        values.append([])
        values[len(values)-1].append("StoragePath")
        values[len(values)-1].append(StoragePath)
        values.append([])
        values[len(values)-1].append("CffFilePath")
        values[len(values)-1].append(CffPath)
        values.append([])
        values[len(values)-1].append("EventContent")
        values[len(values)-1].append(EventContent)
        values.append([])        
        values[len(values)-1].append("JSONCrab")
        values[len(values)-1].append(JSONCrab)
        values.append([])
        values[len(values)-1].append("RunSelection")
        values[len(values)-1].append(RunSelection)

        self.sql.createQuery("INSERT INTO","patuples","",values)

        self.sql.execQuery()

    def insertTopTree(self,user,inputDataSet,PatRef,CMSSWversion,TopTreeVersion,StoragePath,MergedLocation,nEvents,jobEff,CffPath,Comments,EventContent,JSONCrab,RunSelection):

        values = []
        values.append([])
        values[len(values)-1].append("Date")
        values[len(values)-1].append(datetime.date.today().strftime("%Y-%m-%d"))
        values.append([])
        values[len(values)-1].append("User")
        values[len(values)-1].append(user)
        values.append([])
        values[len(values)-1].append("dataset_id")
        values[len(values)-1].append(self.datasetID(inputDataSet))
        values.append([])
        values[len(values)-1].append("patuple_id")
        values[len(values)-1].append(self.patupleID(PatRef))
        values.append([])
        values[len(values)-1].append("StoragePath")
        values[len(values)-1].append(StoragePath)
        values.append([])
        values[len(values)-1].append("TopTreeLocation")
        values[len(values)-1].append(MergedLocation)
        values.append([])
        values[len(values)-1].append("nEvents")
        values[len(values)-1].append(str(nEvents))
        values.append([])
        values[len(values)-1].append("JobEff")
        values[len(values)-1].append(str(jobEff))
        values.append([])
        values[len(values)-1].append("CffFilePath")
        values[len(values)-1].append(CffPath)
        values.append([])
        values[len(values)-1].append("TopTreeVersion")
        values[len(values)-1].append(TopTreeVersion)
        values.append([])
        values[len(values)-1].append("CMSSWversion")
        values[len(values)-1].append(CMSSWversion)
        values.append([])
        values[len(values)-1].append("Comments")
        values[len(values)-1].append(Comments)
        values.append([])
        values[len(values)-1].append("EventContent")
        values[len(values)-1].append(EventContent)
        values.append([])
        values[len(values)-1].append("JSONCrab")
        values[len(values)-1].append(JSONCrab)
        values.append([])
        values[len(values)-1].append("RunSelection")
        values[len(values)-1].append(RunSelection)

        self.sql.createQuery("INSERT INTO","toptrees","",values)

        self.sql.execQuery()

    def insertGENFASTSIM(self,user,PublishName,PNFSPath,CMSSWver,GlobalTag,CFFPath,LHEList,JobEff,nEvents,cycle):

        values = []
        values.append([])
        values[len(values)-1].append("Date")
        values[len(values)-1].append(datetime.date.today().strftime("%Y-%m-%d"))
        values.append([])
        values[len(values)-1].append("User")
        values[len(values)-1].append(user)
        values.append([])
        values[len(values)-1].append("PublishName")
        values[len(values)-1].append(PublishName)
        values.append([])
        values[len(values)-1].append("PNFSPath")
        values[len(values)-1].append(PNFSPath)
        values.append([])
        values[len(values)-1].append("CMSSWver")
        values[len(values)-1].append(CMSSWver)
        values.append([])
        values[len(values)-1].append("GlobalTag")
        values[len(values)-1].append(GlobalTag)
        values.append([])
        values[len(values)-1].append("CffPath")
        values[len(values)-1].append(CFFPath)
        values.append([])
        values[len(values)-1].append("LHEList")
        values[len(values)-1].append(LHEList)
        values.append([])
        values[len(values)-1].append("JobEff")
        values[len(values)-1].append(str(JobEff))
        values.append([])
        values[len(values)-1].append("nEvents")
        values[len(values)-1].append(str(nEvents))
        values.append([])
        values[len(values)-1].append("ProductionCycle")
        values[len(values)-1].append(cycle)
                
        self.sql.createQuery("INSERT INTO","gensims","",values)

        self.sql.execQuery()

    def GenFastSimID(self,PublishName):
        
        options="PublishName REGEXP '"+PublishName+"'"

        self.sql.createQuery("SELECT","gensims","id",options)

        f = open("sql.out","w")
        f.write(self.sql.execQuery())
        f.close()

        for line in open("sql.out","r"):

            #if not repr(line)  == "\n":

            dataSet = line

        os.remove("sql.out")

        #print dataSet.split('\n')[0]

        return dataSet.split('\n')[0]

    def searchPATOrigin(self,patPublishName):

        dataSet = ""

        options="name REGEXP '"+patPublishName+"'"

        self.sql.createQuery("SELECT","patuples","dataset_id",options)

        f = open("sql.out","w")
        f.write(self.sql.execQuery())
        f.close()

        for line in open("sql.out","r"):

            #if not repr(line)  == "\n":

            dataSet = line

        os.remove("sql.out")

        #print dataSet.split('\n')[0]

        return self.datasetName(dataSet.split('\n')[0])

    def datasetID(self,datasetName):

        dataSet = ""

        options="name REGEXP '"+datasetName+"'"

        self.sql.createQuery("SELECT","datasets","id",options)

        f = open("sql.out","w")
        f.write(self.sql.execQuery())
        f.close()

        for line in open("sql.out","r"):

            #if not repr(line)  == "\n":

            dataSet = line

        os.remove("sql.out")

        return dataSet.split('\n')[0]

    def datasetName(self,id):

        dataSet = ""

        options="id = '"+id+"'"

        self.sql.createQuery("SELECT","datasets","name",options)

        f = open("sql.out","w")
        f.write(self.sql.execQuery())
        f.close()

        for line in open("sql.out","r"):

            #if not repr(line)  == "\n":

            dataSet = line

        os.remove("sql.out")

        return dataSet.split('\n')[0]

    def patupleID(self,patupleName):

        dataSet = ""

        options="name REGEXP '"+patupleName+"'"

        self.sql.createQuery("SELECT","patuples","id",options)

        f = open("sql.out","w")
        f.write(self.sql.execQuery())
        f.close()

        for line in open("sql.out","r"):

            #if not repr(line)  == "\n":

            dataSet = line

        os.remove("sql.out")

        return dataSet.split('\n')[0]

#db = topDBInterface()

#print db.searchPATOrigin('/TTbar/mmaes-PAT_TTbar_Summer09-MC_31X_V9_Feb15-v1_13032010_121920-7c4071db814d24e51e1b245b259a972c/USER')

#print db.datasetID('/TTbar2Jets_40GeVthreshold-alpgen/Summer09-MC_31X_V3_7TeV-v2/GEN-SIM-RECO')

#db.insertPatTuple("lol","/TTbar2Jets_40GeVthreshold-alpgen/Summer09-MC_31X_V3_7TeV-v2/GEN-SIM-RECO","/TTbar/mmaes-PAT_TTbar_Summer09-MC_31X_V9_Feb15-v1_13032010_121920-7c4071db814d24e51e1b245b259a972c/USER","abc","def","hij","klm","1","1")

#db.insertTopTree("lol","/TTbar2Jets_40GeVthreshold-alpgen/Summer09-MC_31X_V3_7TeV-v2/GEN-SIM-RECO","/TTbar/mmaes-PAT_TTbar_Summer09-MC_31X_V9_Feb15-v1_13032010_121920-7c4071db814d24e51e1b245b259a972c/USER","abc","def","ghi","jkl","1","mno")

#print db.datasetName("11")

#print db.patupleID("/TTbar/mmaes-PAT_TTbar_Summer09-MC_31X_V9_Feb15-v1_13032010_121920-7c4071db814d24e51e1b245b259a972c/USER")

#db.insertRECO("lol","/TESTRUN_SCRIPT_18102011_153903/mmaes-TESTRUN_SCRIPT_18102011_153903-348ae4446003a8ef5cda190f78cdd378/USER","/rofl","a","b","ccc","jfiiehjpfgez","100","100000","Summer11")

#db.insertGENSIM("lol","/rofl","/PNFS/lala","a","b","ccc","jfiiehjpfgez","100","100000")

#db.GenSimID("/TESTRUN_SCRIPT_18102011_153903/mmaes-TESTRUN_SCRIPT_18102011_153903-348ae4446003a8ef5cda190f78cdd378/USER")
