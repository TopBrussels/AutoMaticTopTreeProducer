# python script to run the skimmer on your own account

# for command line options
from optparse import OptionParser

# regular expressions
import re

# interacting with the os
from subprocess import Popen, PIPE, STDOUT
import sys
import os, os.path

# working with time
import time
from time import strftime, gmtime
from datetime import datetime

# import packages for multi-threading
import Queue
import threading

##################
### LogHandler ###
##################

class logHandler:

    def __init__ (self,fileName):

	self.logFile = fileName

        if not self.logFile == "" and os.path.exists(self.logFile):

            os.remove(self.logFile)

    def output(self,string):
        
        if not self.logFile == "":

            f = open(self.logFile,"a")

            f.write("\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+string)

            f.write("\n")

	    f.close()

	else:

            print "\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+string


###################
### MailHandler ###
###################

# importing smtp lib
import smtplib

class MailHandler:

    def __init__(self,recepient):
        self.smtpServer = "cernmxgwlb4.cern.ch"
#        self.smtpServer = "mach.vub.ac.be"
        #self.smtpServer = "localhost"

        self.senderAddress = "toptreeproducer@mtop.iihe.ac.be"

        #+Popen('hostname', shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip()

        #self.toAnnounce = [ "top-brussels-datasets@cern.ch" ]

        self.toAnnounce = recepient.split(',')
            
    def sendMail(self,subject,msg):

        toAddrs = ""
        
        for to in range(0,len(self.toAnnounce)):
            toAddrs = toAddrs+self.toAnnounce[to]+", "

        m = "From: %s\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (self.senderAddress, toAddrs, subject)
        
        server = smtplib.SMTP(self.smtpServer)
        server.sendmail(self.senderAddress, toAddrs.split(), m+msg)
        server.quit()

#################
## SkimTopTree ##
#################

class SkimTopTree:

    def __init__(self,nSkim,nCycle,filesToSkim):

        self.nSkim = nSkim
        self.nCycle = nCycle
        self.filesToSkim = filesToSkim

    def CompileSkimmer(self):

        global log
        global skimmerDir_base
        global options

        #print "NSKIM: "+str(self.nSkim)
        if self.nSkim == 0:

            # first copy the skimmer dir to a temp one so we can run more than one skim per toptreeproducer

            skimmerDir = skimmerDir_base

            if (debug):
                print "DEBUG: copying skim dirs from " + productionrelease+options.ttprodlocation+"/skimmer"  + " to " + str(skimmerDir)

#this command seems to fail ??? the code does not end up in the skimmer dir
            Popen("cp -vfr "+productionrelease+options.ttprodlocation+"/skimmer/* "+skimmerDir  +"/", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
#            Popen("cp -vfr "+ skimmerDir  + "/skimmer "+skimmerDir, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

            if (debug):
                print "DEBUG: Skimmerdir created? : " + str (os.path.exists(skimmerDir))

            # now compile it

            init = initROOT+"cd "+skimmerDir

            log.output("-> Compiling TopTreeProducer and Running the skimmer")

            # check if the makefile is ok
            
            m32flag = bool(False)
            m32flagSkim = bool(False)
            lRFIOflag = bool(False)
            
            print "searching in skimmer dir = " + str(skimmerDir)
            
            for line in open(skimmerDir+"/../src/Makefile","r"):
                if not line.rfind("g++ -m32") == -1:
                   # m32flag = bool(True)
                    print "m32 falg set"
                if not line.rfind("-lRFIO") == -1:
                    lRFIOflag = bool(True)
                    print "rfio falg set"

#commenting this out
#            for line in open(skimmerDir+"/Makefile","r"):
#                if not line.rfind("g++ -m32") == -1:
#                    m32flagSkim = bool(True)      



 #           if not options.mtop and not m32flag:
 #               if(debug):
 #                   print "DEBUG: changing to skimmer directory 1"
 #               log.output("    -----> Adding -m32 flag to the TopTreeProducer MakeFile")
 #               cmd = 'cd '+skimmerDir+'/../src; sed -e \'s/g++/g++ -m32/\' Makefile >> Makefile.tmp; mv Makefile.tmp Makefile'
 #               pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
 #               out = pExe.stdout.read()

            if lRFIOflag:
                if(debug):
                    print "DEBUG: changing to skimmer directory 2"
                log.output("    -----> Removing -lRFIO flag from the TopTreeProducer MakeFile")
                cmd = 'cd '+skimmerDir+'/../src; sed -e \'s/-lRFIO/ /\' Makefile >> Makefile.tmp; mv Makefile.tmp Makefile'
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                out = pExe.stdout.read()

            if not options.mtop and  not m32flagSkim:
                if(debug):
                    print "DEBUG: changing to skimmer directory 3" + str(skimmerDir)
                log.output("    -----> Adding -m32 flag to the TopSkimmer MakeFile")
 #               cmd = 'cd '+skimmerDir+'; sed -e \'s/g++/g++ -m32/\' Makefile >> Makefile.tmp; mv Makefile.tmp Makefile; cat Makefile'
                cmd = 'cd '+skimmerDir+';'

                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                out = pExe.stdout.read()
                
#simplifying compile statement
            compile="; cd ../src; pwd ;echo $ROOTSYS ; make clean; make; cd -;echo ' Now in dir: '; pwd; ls; "

#cp -vf ../src/*.so .; make clean; make"
           

#            cmd = init+';export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.'+compile+'; rm -v TopSkim; g++ `root-config --ldflags` -L `pwd` -l TinyXML -l Toto -I `root-config --incdir` `root-config --libs` TopSkim.C -o TopSkim'

#            cmd = init+';export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.'+compile+' rm -v TopSkim; g++ -std=c++11 -L `pwd` -l TinyXML -l Toto -I `root-config --incdir` `root-config --libs` TopSkim.C -o TopSkim'

            cmd = init+';export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.'+compile+' rm -v TopSkim; g++ -std=c++11 -L `pwd` -l TinyXML -l Toto -I `root-config --incdir` `root-config --libs` TopSkim.C -o TopSkim; ls'

            #cmd = ""
            log.output(cmd)

            pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

            out = pExe.stdout.read()

            if (debug):
                print "DEBUG: output of compilation -  -  " + str(out) 

            while True:
                line = pExe.stdout.readline()
                log.output(line.strip())
                if not line: break

    def SkimTopTree(self,log,skimmerDir):

        global nOutput
        global nInput
        global nCycles
        global RootInstallation
        global userName
        global nFailedJobs
        global options

        log.output("-> Processing Skim: "+str(self.nCycle+1)+"/"+str(nCycles))

        # make a skimmer dir for this skim thread

        if (debug1):
            print "DEBUG:SkimTopTree: making a skimmer dir for this thread () skimmerdir = " + str(skimmerDir)

        Popen("mkdir "+skimmerDir, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
        Popen("cp -vfr "+productionrelease+options.ttprodlocation+"/"+timestamp+"_skimmer/* "+skimmerDir + "/", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

#        Popen("cp -vf DownloadSample.sh "+skimmerDir, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

        # cleaning the skimmer dir
            
        if (debug1):
            print "DEBUG1: cd to skimmerDir and ls " + skimmerDir
        init = initROOT+" export DCACHE_RAHEAD=\"1\"; export DCACHE_RA_BUFFER=\"250000000\"; cd "+skimmerDir+' ls;'

        pExe = Popen(init, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read() # this cleans the directory
        if (debug1):
            print "DEBUG: With the output " + pExe


        log.output("   ----> Step 1: Running the skimmer")

        # create the skim.xml
        if (debug1):
            print "DEBUG: Opening the skim.xml... "

        tmpXML = open(skimmerDir+"/"+timestamp+"_skim_thread.xml","w")

#        tmpXML = open("thisisthetest_skim.xml","w")


#        if (debug):
#            print "DEBUG: Writing the skim xml to:  " + str(skimmerDir+"/"+timestamp+"_skim.xml")
#            print " "
#            print "These are the files to skim: "
        tmpXML.write("<?xml version=\"1.0\"?>\n\n<inputdatasets>\n\n")
        for i in xrange(len(self.filesToSkim)):

            if not options.usesrmcp:
#                print "\t <i file=\"dcap://maite.iihe.ac.be/"+self.filesToSkim[i]+"\"/>\n"
                tmpXML.write("\t <i file=\"dcap://maite.iihe.ac.be"+self.filesToSkim[i]+"\"/>\n")
#                tmpXML.write("\t <i file=\"file:"+self.filesToSkim[i]+"\"/>\n")
            else:
                arr=self.filesToSkim[i].split("/")
                file=arr[len(arr)-1]
                tmpXML.write("\t <i file=\""+file+"\"/>\n")

        tmpXML.write("\n</inputdatasets>\n\n")
            
        for line in open(options.xml,"r"):
                
            line = line.strip()
        
            if not line == "":
                if line.rfind("<!--") == -1 and line.rfind("<?xml") == -1 and line.rfind("inputdatasets") == -1 and line.rfind("i file=") == -1:

                    if not line.rfind("<o ") == -1 or not line.rfind("<k type") == -1:
                        tmpXML.write("\t"+line.replace(".root","_"+str(self.nSkim)+".root")+"\n")
                    elif not line.rfind("</") == -1:
                        tmpXML.write("\n"+line+"\n\n")
                    else:
                        tmpXML.write(line+"\n\n")
                        
        tmpXML.close()
        if (debug):
            print "The emp skim xml should be written to: " + str(skimmerDir)+"/"+timestamp+"_skim_thread.xml"


        # run the skimmer
        if (debug1):
            print "DEBUG: Running the skimset "

        out=[]
        runOK = bool(False)
        if not options.pbs:
            if (debug1):
                print "DEBUG: Not running pbs "   
         
            cmd = init+'rm *.root -v'  
            pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

            if  options.usesrmcp:

                if (debug1):
                    print "DEBUG: Running usesrmcp "
                log.output(" ----> SRMCP option was declared so downloading rootfiles first and skimming on them locally")

                InputFiles = ""
                for i in self.filesToSkim:
                    InputFiles=InputFiles+i.split("/")[len(i.split("/"))-1]+","
                    if (debug1):
                        print "DEBUG: looping input files "

                InputFiles = InputFiles.strip(",")

                cmd = init+"sh DownloadSample.sh "+options.location+" "+InputFiles

                #print cmd
                                
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

                while True:
                    line = pExe.stdout.readline()
                    log.output(line.strip())
                    if not line: break

#            print "DEBUG: This is the command(s) for running the skim thread: " + str(cmd) 

          #  cmd = init+'mv -v '+timestamp+'_skim_thread.xml skim.xml; cat skim.xml; export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.; echo $LD_LIBRARY_PATH; ./TopSkim; rm -v skim.xml'


            print "DEBUG: This is the directory we are in for skimming: " + str(os.getcwd()) + "  skimmerDir is currently "+ skimmerDir
 
            cmd = 'cd '+ skimmerDir  +'; pwd; ls; mv -v '+timestamp+'_skim_thread.xml skim.xml; cat skim.xml; export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.; echo $LD_LIBRARY_PATH; ./TopSkim; rm -v skim.xml'


            #cmd = init+';export DCACHE_RA_BUFFER="400000000"; export'
            if (debug1):
                print "DEBUG: finally running the skim exe"

            pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            pout = pExe.stdout.readline()

            if (debug1):
                print "DEBUG: with the following output: " + str(pout)

            while True:
                line = pExe.stdout.readline()
                if line.strip().rfind("Warning in <TVector3::PseudoRapidity>:") == -1:
                    log.output(line.strip())
                out.append(line)
                if not line: break
           

            runOK = bool(False)

            for line in out:
                if not line.rfind("--> Skimmed") == -1:
                    splittedLine = line.split(" ")                    
                    #nOutput += int(splittedLine[2])
                    #nInput += int(splittedLine[8])
                    print "incrementing stats" + str(nOutput) + "  " + str(nInput)

        else:

            log.output("    -----> Submitting this TopSkim on the PBS localgrid queue")

            if not os.path.exists("/localgrid/"+userName+"/root"):

                log.output("    -----> /localgrid/"+userName+"/root does not exist, copying "+RootInstallation)

                Popen("cp -vfr "+RootInstallation+" /localgrid/"+userName+"/root", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read() #copy root installation to localgrid so the WNs can use it

            # copy our temp skimmer dir to localgrid

            copy = Popen("cp -vfr "+skimmerDir+" /localgrid/"+userName+"/", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
            log.output(copy)

            # copy our proxy to localgrid if the WN needs to copy to PNFS

            if not options.publishName == "NONE":

                 Popen("cp -vfr $X509_USER_PROXY /localgrid/"+userName+"/grid-proxy_"+timestamp, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
                
            # create pbs script

            pbsFile = "/localgrid/"+userName+"/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+".pbs"

            log.output(skimmerDir+" "+pbsFile)
            
            pbs = open(pbsFile,"w")

            taskName=skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"_job"+str(self.nCycle+1)
            
            pbs.write("#! /bin/bash\n")
            pbs.write("#PBS -l walltime="+str(options.walltime)+"\n")
            pbs.write("#PBS -r n\n")
            pbs.write("#PBS -N "+taskName+"\n")
            #pbs.write("#PBS -o "+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+".out\n")
            pbs.write("#PBS -j oe\n")
            pbs.write("#PBS -k oe\n")
            pbs.write("#PBS -l nodes=1\n")

            pbs.write("echo dumping some info on the worker node\n")
            pbs.write("hostname\n")
            pbs.write("df -h\n")
            pbs.write("uptime\n")
            pbs.write("free\n")

            pbs.write("echo \"\"\n")
            pbs.write("echo Checking storage routes on $(hostname)\n")
            pbs.write("echo \"\"\n")
            pbs.write("/sbin/route | grep behar\n")
            pbs.write("echo \"Number of routes:$(/sbin/route | grep behar | wc -l)\"\n")
            pbs.write("echo \"\"\n")

            #Not needed anymore when using lcg-cp, now you copy certificate
            #if not options.publishName == "NONE":
                #pbs.write("export X509_USER_PROXY=\"$HOME/grid-proxy_"+timestamp+"\"; voms-proxy-info\n")

            pbs.write("export DCACHE_RA_BUFFER=\"250000000\"\n")

            pbs.write("export ROOTSYS=\"/localgrid/"+userName+"/root\"\n")
            pbs.write("export PATH=$PATH:$ROOTSYS/bin\n")
            pbs.write("export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ROOTSYS/lib\n")
            pbs.write("source /jefmount_mnt/jefmount/cmss/slc5_amd64_gcc434/external/dcap/2*/etc/profile.d/init.sh") # to fix the fact that the WN's dont have 64bit libdcap
            # DEBUG BEGIN Greg 07/11/2013
            #pbs.write("\n echo \"Results of ls -la /scratch :\" \n")
            #pbs.write("ls -la /scratch \n")
            # DEBUG END Greg 07/11/2013
            # DEBUG BEGIN Greg 14/11/2013
	    pbs.write("echo \" PWD : \" \n")
	    pbs.write("pwd \n")
            # DEBUG END Greg 14/11/2013
            pbs.write("\nmv -f "+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+" /scratch/$PBS_JOBID/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"\n")
            pbs.write("\ncd /scratch/$PBS_JOBID/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"\n")
            pbs.write("export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.\n")
            pbs.write("mv "+timestamp+"_skim_thread.xml skim.xml; ls -ltr\n")

            if  options.usesrmcp:

                log.output(" ----> SRMCP option was declared so downloading rootfiles first and skimming on them locally")
                
                InputFiles = ""
                for i in self.filesToSkim:
                    InputFiles=InputFiles+i.split("/")[len(i.split("/"))-1]+","

                InputFiles = InputFiles.strip(",")

                pbs.write("sh DownloadSample.sh "+options.location+" "+InputFiles+"\n")

                
            
            pbs.write("./TopSkim\n")

            if options.publishName == "NONE":

                pbs.write("\ncd /scratch/$PBS_JOBID/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"\n")
                pbs.write("mkdir -v tmpscratch \n")
                pbs.write("mv -v *Skimmed*.root tmpscratch \n")
                pbs.write("rm -v *.root \n")
                pbs.write("mv -v tmpscratch/* .\n")
                pbs.write("rmdir -v tmpscratch \n")
                pbs.write("cd - \n")
                
                pbs.write("\nmv -f /scratch/$PBS_JOBID/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+" $HOME/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"\n")

            else:
                pbs.write("\nrootFile=$(cd /scratch/$PBS_JOBID/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"; ls *Skimmed*.root); echo $rootFile\n")
                #pbs.write("\necho srmcp file:////scratch/$PBS_JOBID/"+skimmerDir.split("/")[1]+"/$rootFile "+srm+destination+"/$rootFile\n")
                pbs.write("\necho \"Local file:\"")
                pbs.write("\ndu -sh /scratch/$PBS_JOBID/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"/$rootFile")
                #pbs.write("\nsrmcp file:////scratch/$PBS_JOBID/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"/$rootFile "+srm+destination+"/$rootFile\n")
		pbs.write("\necho \"Certificate info:\"")
		pbs.write("\necho \'$X509_USER_CERT: \'$X509_USER_CERT")
		pbs.write("\necho \'$X509_USER_PROXY: \'$X509_USER_PROXY")
		pbs.write("\nls -la $X509_USER_PROXY")
		pbs.write("\necho \'User ID ($UID): \'$UID")
		pbs.write("\necho \'Copy certificate to /tmp/x509up_u$UID\'")
		pbs.write("\ncp $HOME/grid-proxy_"+timestamp+" /tmp/x509up_u$UID")
		pbs.write("\nls -la /tmp/x509up_u$UID")
		pbs.write("\necho \"Changing certificate permissions to 600\"")
		pbs.write("\nchmod 600 /tmp/x509up_u$UID")
		pbs.write("\nls -la /tmp/x509up_u$UID")
		#pbs.write("\necho \"Environment :\"")
		#pbs.write("\nenv")
		pbs.write("\necho \"Copy file to pnfs using lcg-cp:\"")
                #pbs.write("\nlcg-cp -v file:///scratch/$PBS_JOBID/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"/$rootFile "+srm+"/srm/managerv2?SFN="+destination+"$rootFile\n")
                pbs.write("\nlcg-cp -v file:////scratch/$PBS_JOBID/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"/$rootFile "+srm+"/srm/managerv2?SFN="+destination+"$rootFile\n")
		#pbs.write("\nls -la /tmp/")
		#pbs.write("\necho \"Remove certificate copy in /tmp\"")
		#pbs.write("\nrm -f /tmp/x509up_u$UID")
		#pbs.write("\nls -la /tmp/")
                pbs.write("\necho \"File on storage:\"")
                pbs.write("\ndu -sh "+destination+"$rootFile")

                pbs.write("\nif [ ! -f \""+destination+"$rootFile\" ];then")
                pbs.write("\n\techo \"Failed to copy Skimmed File to PNFS!\"")
                pbs.write("\nfi")
                
            pbs.write("\n echo THIS IS THE END\n")

            pbs.close()

            #submit the job

            pExe = Popen("cd /localgrid/"+userName+"/; qsub -q localgrid@cream02.iihe.ac.be "+pbsFile, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

            pbsID=pExe.stdout.read()

            log.output("PBS Job ID: "+pbsID)

            logPBS = (Popen("echo /localgrid/"+userName+"/"+taskName+".o*", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()).strip()

            log.output("PBS RealTime LogFile: "+str(logPBS))

            #sys.exit(0)

            #time.sleep(60)

            #check pbs job (old method)
            
            #while not os.path.exists("/localgrid/"+userName+"/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+".out"):
                
            #    log.output("     -----> It seems that the job is still running, sleeping 60s")
            #    time.sleep(60)

            # check pbs job (new method)

            # OLD NON-INTERACTIVE ROUTINE
            status = Popen("qstat "+pbsID, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
        
            while status.find("Unknown Job Id") == -1:

                if pbsID.rfind("cream02") == -1:

                    log.output("     -----> It seems that the job failed to submit, resubmitting and then sleeping for "+str(60)+"s")
                    
                    pExe = Popen("cd /localgrid/"+userName+"/; qsub -q localgrid@cream02.iihe.ac.be "+pbsFile, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

                    pbsID=pExe.stdout.read()
                    
                    log.output("PBS Job ID: "+pbsID)

                    time.sleep(60)

                    status = Popen("qstat "+pbsID, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

                else: 
                    log.output("     -----> It seems that the job is still running, sleeping "+str(60)+"s")
            
                    time.sleep(60)

                    status = Popen("qstat "+pbsID, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

            log.output("     -----> Job has finished, parsing logfile")

            # NEW METHOD WITH REALTIME PBS LOG READING

            #PIDtail=0
            #while True:

            #    status = Popen("qstat "+pbsID, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

            #    if not status.find("Unknown Job Id") == -1: break

            #    logPBS = (Popen("echo /localgrid/"+userName+"/"+taskName+".o*", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()).strip()

            #    if os.path.exists(logPBS):

            #        log.output("     -----> It seems that the job has started, attaching to real-time logfile")

            #        pExe = Popen("tail -f "+logPBS, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

            #        PIDtail = pExe.pid

            #        while True:
            #            line = pExe.stdout.readline()
            #            if line.strip().rfind("Warning in <TVector3::PseudoRapidity>:") == -1:
            #                log.output(line.strip())
            #
            #            status = Popen("qstat "+pbsID, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
            #            if not status.find("Unknown Job Id") == -1:
            #                break
            
            #    else:
                    
            #        log.output("     -----> It seems that the job is still pending, sleeping "+str(60)+"s")
                    
            #        time.sleep(60)
        
            #logfile = open("/localgrid/"+userName+"/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+".out","r")

            #Popen("kill -9 "+str(PIDtail), shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
            
            #log.output("     -----> Job has finished, parsing logfile")

            logPBS=(Popen("echo /localgrid/"+userName+"/"+taskName+".o*", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()).strip()
            logfile = open(logPBS,"r")
            
            for line in logfile:
                if line.strip().rfind("Warning in <TVector3::PseudoRapidity>:") == -1:
                    log.output(line.strip())
                    out.append(line.strip())

            # move back the rootfile and remove the dir on localgrid

            log.output(Popen("mv /localgrid/"+userName+"/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+"/*.root "+skimmerDir+" -v; rm -rfv /localgrid/"+userName+"/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1], shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read())

            # remove pbs config and output files

            os.remove(pbsFile)
            #os.remove("/localgrid/"+userName+"/"+skimmerDir.split("/")[len(skimmerDir.split("/"))-1]+".out")
            os.remove(logPBS)
            
        for line in out:

            if not line.rfind("--> Skimmed") == -1:
                
                splittedLine = line.split(" ")
                    
                nOutput += int(splittedLine[2])
                nInput += int(splittedLine[8])
                print "incrementing stats"
                    
            if not line.rfind("Code running was succesfull!") == -1 and nInput > 0:

                runOK = bool(True)

            if not line.rfind("Failed to copy Skimmed File to PNFS") == -1:

                runOK = bool(False)

                log.output("     -----> Job encountered problem while copying output file to PNFS")


        if not runOK:
            
            log.output("     -----> It seems that the job failed")

            nFailedJobs = nFailedJobs+1

        return runOK

    def CopyTopTree(self,log,skimmerDir):

        if(debug1):
            print"DEBUG: In copyTopTree"

        global TopSkimDir
        global destination
        global timestamp
        global options
        global srm
        global userName
        global url

        fileID = int(self.nCycle+1)
        
        if options.publishName == "NONE":

            log.output(" --> Step 2: Copy the output to Skimmed/"+timestamp)
            # move skimmed file to the website appdir
            
            toptree = "*_"+str(fileID)+".root"

            #log.output(Popen('ls -ltr '+TopSkimDir+'/'+skimmerDir, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read())

            if not options.mtop:
                log.output(Popen('mv -v '+TopSkimDir+'/'+skimmerDir+'/'+toptree+' '+destination+"/", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read())

            else: # for mtop http download we need to have the files with proper timestamp

                log.output("  ---> Storing "+destination+"/TopTree_Skimmed_"+str(timestamp)+"_"+str(fileID)+".root")
                
                log.output(Popen('mv -v '+TopSkimDir+'/'+skimmerDir+'/'+toptree+' '+destination+"/TopTree_Skimmed_"+str(timestamp)+"_"+str(fileID)+".root", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read())

                log.output(" ---> Updating permissions (-rw-r--r--) for "+destination+"/TopTree_Skimmed_"+str(timestamp)+"_"+str(fileID)+".root")

                log.output(Popen("chmod -v 644 "+destination+"/TopTree_Skimmed_"+str(timestamp)+"_"+str(fileID)+".root", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read())

                url += "\thttps://mtop.iihe.ac.be/TopDB/toptrees/getfile/"+timestamp+"_"+str(fileID)+"\n"

            # remove the temp skimmer dir at the end

            Popen("rm -vfr "+skimmerDir, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()
            
            if not int(pExe.poll()) == 0:
                log.output(cmd)
                log.output(out)

            return int(pExe.poll())
        
        else:

            if not options.pbs: # if it's on pbs with publish, we let the WN's do the srmcp
                         
                log.output(" --> Step 2: Not running PBS, so transfering the output from WorkerNode to PNFS: "+dest)
                if(debug1):
                    print"***"
                    print "DEBUG:  transeferring skimmed trees: "
                    print "    TopSkimDir = " + str(TopSkimDir)
                    print "    skimmerDir = " + str(skimmerDir)
                    

#                rootfile = Popen('ls '+TopSkimDir+'/'+skimmerDir+'/*_'+str(fileID)+'.root', shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip()

                rootfile = Popen('ls ' + skimmerDir + '/*_'+str(fileID)+'.root', shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip()
                if(debug1):
                    print "    output of ls :  " +  rootfile 

     
                #cmd = 'srmcp file:////'+rootfile+" "+srm+dest+"/"+rootfile.split("/")[len(rootfile.split("/"))-1]
                cmd = 'lcg-cp -v file:////'+rootfile+" "+srm+"/srm/managerv2?SFN="+dest+"/"+rootfile.split("/")[len(rootfile.split("/"))-1]

                log.output(cmd)
                log.output(Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip())
            
        # remove the temp skimmer dir at the end

        Popen("rm -vfr "+skimmerDir, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

        return 0

##############
## WorkFlow ##
##############

class WorkFlow (threading.Thread ):

    def __init__(self, nThread, *args, **kwds):

        global options
        global log

        self.nThread = nThread        

        threading.Thread.__init__(self, *args, **kwds)
    
        self.keepAlive = bool(True)

        if int(options.nWorkers) == 1:
            self.log = log
        else:
            self.log = logHandler("logs/log_"+timestamp+"_thread"+str(self.nThread)+".txt")

    def stop (self):
        
        self.keepAlive = bool(False)

    def run (self):

        global options
        global nCycles
        
        # our thread runs forever
        
        while not skimPool.empty():

            #print self.nThread

            skim = skimPool.get()

            if int(options.nWorkers) == 1:
                log.output("-> Thread "+str(self.nThread)+" Processing Skim: "+str(skim.nCycle+1)+"/"+str(nCycles))
            else:
                if not options.mtop:
                    log.output("-> Thread "+str(self.nThread)+" Processing Skim: "+str(skim.nCycle+1)+"/"+str(nCycles)+" (LogFile: "+self.log.logFile+")")
                else:
                    log.output("-> Thread "+str(self.nThread)+" Processing Skim: "+str(skim.nCycle+1)+"/"+str(nCycles)+" (LogFile: https://mtop.iihe.ac.be/TopDB/toptrees/getlog/"+str(timestamp)+"_thread"+str(self.nThread)+")")
                    
            skimmerDir = productionrelease+options.ttprodlocation+"/"+timestamp+"_skimmer_thread"+str(self.nThread)


            if (skim.SkimTopTree(self.log,skimmerDir)  == True or skim.SkimTopTree(self.log,skimmerDir) == False ):
                if(debug1):
                    print"DEBUG: Will try to copy toptree"

                skim.CopyTopTree(self.log,skimmerDir)

                log.output("-> Thread "+str(self.nThread)+" Finished Skim: "+str(skim.nCycle+1)+"/"+str(nCycles))

            else:

                log.output("-> Thread "+str(self.nThread)+" had a failed TopSkim: "+str(skim.nCycle+1)+"/"+str(nCycles))
                

            #time.sleep(10)


###############
### METHODS ###
###############

def checkGridProxy ():

    global log

    log.output("* Checking GRID proxy")
        
    cmd = 'voms-proxy-info'
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    
    lines = output.split('\n')
        
    #print lines

    if lines[1] == "Couldn't find a valid proxy.":
        
        log.output(" ---> No Valid GRID proxy was retrieved, please use voms-proxy-init --voms cms:/cms/becms --valid 190:00 before running the skimmer.")
        
        sys.exit(1)
        
    else:

        for i in xrange(len(lines)):
            
            if not lines[i].rfind("timeleft") == -1:
                
                timeleft = lines[i].split("timeleft  : ")
                
                splittedtimeLeft = timeleft[1].split(":");
                
                if int(splittedtimeLeft[0]) < 50:
                    
                    log.output(" ---> GRID proxy is valid < 50h, please renew it using voms-proxy-init --voms cms:/cms/becms --valid 190:00 before running the skimmer.")
                    
                    sys.exit(1)

                else:
                        
                    log.output(" ---> Valid GRID proxy was found (Valid for "+str(timeleft[1])+")")

def CheckDuplicateFiles(dir):
    
    global log
    
    log.output("* Checking "+dir+" for duplicated files")
   
    toRM = ""

    n=0

    min=9999
    max=-9999
    for i in os.listdir(dir):

        if i.rfind(".root") == -1:
            continue

        n=n+1

        num1 = i.split("_")[1]
        num = num1.split(".")[0]
        log.output("* Found: " + str(i))

        if int(num) > max: max=int(num)
        if int(num) < min: min=int(num)
        
    #print min
    #print max
    #sys.exit(1)

    m=0
    p=0

    for i in xrange(min,max+1):
        m=m+1

    for i in xrange(min,max+1):
        
        ## LOOKING FOR DUPLICATE FILES
            
        #splitName = i.split("_")[3]

        #if int(splitName) < 500 or int(splitName) > 520 : continue

        #if not i == 1089: continue

        splitName = str(i)

        cmd = "ls -t "+dir+" | grep root | grep TOPTREE_"+splitName+"_"

        pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        out = pExe.stdout.read()

        #print out
        
        fileList = out.split("\n")

        #print str(i)+" "+str(len(fileList)-1)

        if len(fileList)-1 == 0:

            log.output("---> NO ROOT FILE FOUND FOR JOB "+splitName)

            p=p+1

            continue
        
        if not len(fileList)-1 == 1:

            log.output("  ---> Job "+str(i)+" might have duplicateded files -> "+str(fileList))
            
            ## CHECK WHICH IS THE LATEST RESUBMIT
            
            highest = int(0);

            for duplicate in fileList:

                nSubmit = ""

                if not duplicate == "":

                    if  not len(duplicate.split("_")[4].split(".root")) == 1:
                        
                        nSubmit = duplicate.split("_")[4].split(".root")[0]

                    else:

                        nSubmit = duplicate.split("_")[4]

                    #print nSubmit
                    
                    if int(nSubmit) > highest:

                        highest = int(nSubmit)

            #print highest

            # remove all submissions below nSubmit

            highestIndexList = []

            for duplicate in fileList:

                if not duplicate == "":

                    nSubmit = ""

                    if  not len(duplicate.split("_")[4].split(".root")) == 1:
                        
                        nSubmit = duplicate.split("_")[4].split(".root")[0]

                    else:

                        nSubmit = duplicate.split("_")[4]

                    #print nSubmit+" "+str(highest)

                    if int(nSubmit) < highest:

                        if toRM.rfind(duplicate) == -1:
                        
                            toRM += duplicate+";"

                            log.output("   ----> Adding file "+duplicate+" to the list of files to be ignored")

                    elif int(nSubmit) == highest:

                        highestIndexList.append(duplicate)

            if len(highestIndexList) > 1:

                log.output("  ---> It seems the highest Submission index is also duplicated "+str(highestIndexList));

                for j in xrange(1,len(highestIndexList)):

                    toRM += highestIndexList[j]+";"
                    log.output("   ----> Adding file "+highestIndexList[j]+" to the list of files to be ignored")


    if toRM == "":

        log.output("   ----> NO duplicated files found in this sample!")

    log.output("***** DUPLICATE CHECK SUMMARY *****")
    log.output("Inspected job numbers: "+str(min)+" -> "+str(max))
    log.output("Number of files checked: "+str(n))
    log.output("Number of duplicates found: "+str(len(toRM.split(";"))-1))
    log.output("Number of files to be skimmed: "+str(n-(len(toRM.split(";"))-1)))
    log.output("Number of jobs: "+str(m))
    log.output("Number of jobs without ROOT file: "+str(p))
    
    return toRM

###############
### OPTIONS ###
###############

optParser = OptionParser()

optParser.add_option("-l","--toptree_location", dest="location",default="None",
                     help="TopTree storage path on PNFS", metavar="")

optParser.add_option("-t","--toptreeproducer", dest="ttprodlocation",default="TopTreeProducer",
                     help="TopTreeProducer directory", metavar="")

optParser.add_option("-s","--skim_xml", dest="xml",default="None",
                     help="TopTree tag", metavar="")

optParser.add_option("-n","", dest="nFilesPerSkim",default=10,
                     help="Number of files to skim during one skim cycle (-1: all files in one job)", metavar="")

optParser.add_option("-j","", dest="nWorkers",default=1,
                     help="Number of threads", metavar="")

optParser.add_option("-w","--walltime", dest="walltime",default="36:00:00",
                     help="Define the PBS job walltime.", metavar="")

optParser.add_option("-p","--publish", dest="publishName",default="NONE",
                     help="Publish your skim to PNFS", metavar="")

optParser.add_option("-a","--announce", action="store_true", dest="announce",default=bool(False),
                     help="Announce production to the mailing list (only works with -p)", metavar="")

optParser.add_option("","--email", dest="email",default="top-brussels-datasets@cern.ch",
                     help="Change the email address for announcement from top-brussels-datasets to another email", metavar="")

optParser.add_option("-o","--log-stdout", action="store_true", dest="stdout",default=bool(False),
                     help="Write the main log file to the stdout", metavar="")

optParser.add_option("","--use-pbs", action="store_true", dest="pbs",default=bool(False),
                     help="Submit the skim jobs on the localgrid PBS system", metavar="")

optParser.add_option("","--srmcp", action="store_true", dest="usesrmcp",default=bool(False),
                     help="Use SRMCP on the WNs to download rootfiles first from SE. If false, libDcap is used.", metavar="")

optParser.add_option("","--mtop-runmode", action="store_true", dest="mtop",default=bool(False),
                     help="DO NOT USE THIS OPTION", metavar="")

optParser.add_option("","--mtop-setuser", dest="mtopuser",default="dhondt",
                     help="DO NOT USE THIS OPTION", metavar="")


    
(options, args) = optParser.parse_args()
    
if options.location == "None":
    
    print "For the options look at python SkimTopTree.py -h"
    sys.exit(1)

if options.mtop:

    host = Popen('hostname', shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip()

    if not host == "mtop.iihe.ac.be" and not host == "mtop2.iihe.ac.be":

        print "You are running on "+host+", this is NOT mtop and yet you use --mtop-runmode????!!!!"

        sys.exit(0)

if options.announce and options.publishName == "NONE":

    print "Option -a can only be used together with option -p"

    sys.exit(0)

############
### MAIN ###
############

## SETTINGS

#RootInstallation = "/user/cmssoft/root_5.26.00e_iihe_default_dcap/root"
#RootInstallation = "/Software/LocalSoft/root"
#RootInstallation = "/Software/LocalSoft/root_5.30.02/root"
#RootInstallation = "/cvmfs/cms.cern.ch/slc6_amd64_gcc491/lcg/root/6.02.00-odfocd2/"
RootInstallation = "/user/keaveney/public_html/root6/root-6.02.10/"

storage_dest = "Skimmed-TopTrees" # (relative to /pnfs/iihe/cms/store/<username>/)

srm="srm://maite.iihe.ac.be:8443"

## Do not edit below
    
nSkim = int(1)

url = ""

# get current dir
cmd = 'pwd'
pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
TopSkimDir = pExe.stdout.read().strip()
debug = False
debug1 = True

# get username

userName = Popen('echo $USER', shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip()

PNFSUserName = userName

if options.mtop:

    userName = "dhondt"

    PNFSUserName = options.mtopuser

    options.announce = True # mtop allways announces

    #options.publishName = "NONE"

timestamp = strftime("%d%m%Y_%H%M%S") # need a timestamp for dirs and logfiles

#productionrelease = "/home/dhondt/ProductionReleases/"
productionrelease=""

skimmerDir_base = productionrelease+options.ttprodlocation+"/"+timestamp+"_skimmer" # this is the dir where we'll compile the topskim
if (debug):
    print "Skimmer will be compiled in (skimmerDir_base): " +  str(skimmerDir_base)
Popen("mkdir "+skimmerDir_base, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

if (debug):
    print "DEBUG: Skkm base dir created? : " + str (os.path.exists(skimmerDir_base))

# setup root

initROOT = "export ROOTSYS=\""+RootInstallation+"\"; export PATH=$PATH:$ROOTSYS/bin; export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ROOTSYS/lib:/sandbox/cmss/slc5_amd64_gcc434/cms/cmssw/CMSSW_4_2_8/external/slc5_amd64_gcc434/lib;"
#"export LD_LIBRARY_PATH=\"/opt/d-cache/dcap/lib:/opt/glite/lib:/opt/glite/lib64:/opt/globus/lib:/opt/lcg/lib:/opt/lcg/lib64:/opt/log4cpp/lib:/opt/external/usr/lib:/opt/external/opt/c-ares/lib:/opt/classads/lib64/\"; 

# logging

if not options.stdout:
    log = logHandler("logs/log_"+timestamp+".txt")
else:
    log = logHandler("")


nInput = int(0)
nOutput = int(0)

nFailedJobs = int(0)

# start the loop

log.output("*** StandAlone TopTree Skimmer ***")

if (debug):
    print "Starting the loop"

if options.mtop:
    log.output("* Request comes from: "+options.email)

    if (debug):
        print "DEBUG: MTOP MODE ON!"
 
if not options.mtop: # for now we don't use pbs stageout on mtop and thus need no proxy
    print "DEBUG: checking grid proxy "
    checkGridProxy()

# check if more than one path is provided

if (debug):
    print "DEBUG: checking paths"


paths = options.location.split(",")

if (debug):
    print "DEBUG: PATHS are:" + str(paths)

for path in paths:    
    log.output("* Skimming toptree files inside "+path)

    if (debug):
        print "DEBUG: Toptrees to be skimmed are in: " + path

destination = ""
if options.publishName == "NONE" and (not options.announce or options.mtop):

    # build destination folder name for local staging

    if not options.mtop:
        destination = TopSkimDir+"/Skimmed/"+timestamp
        pos = options.location.find('user')
        split = (paths[0])[pos:-1].split('/')
        
        for i in range ( 2 , len(split)-2 ):
            
            destination +=  "-"+split[i]

    else:
        
        destination = TopSkimDir+"/Skimmed/" # http place for mtop
        print "DEBUG: Skimmed toptrees will end up in:  " + str (destination)

    if not os.path.exists(destination):
        os.mkdir(destination)

    log.output("* The output will be stored inside: "+destination)

# now doing the work

fileList = []

duplicates = ""
for path in paths:
    tmpduplicates=CheckDuplicateFiles(path)
    if not tmpduplicates == "":
        duplicates = duplicates+";"+tmpduplicates

#print duplicates
#sys.exit(0)

for path in paths:

    for i in os.listdir(path):
        if(debug):
            print "DEBUG: looping file: " + str(i)

        if not i.rfind(".root") == -1:
        #if not i.rfind("35_1_z8z.root") == -1:

            if duplicates.rfind(i) == -1:
            
                fileList.append(path+"/"+i)

#print fileList[0]

#print len(fileList)

if not duplicates == "":

    log.output("* WARNING: It seems that some files in this production are duplicated. This will NOT affect your skim as duplicated files are removed from the list of files to skim. However, you should report this issue to the TopTree Production team so they can remove the duplicated files.")

    time.sleep(20)
    
if options.nFilesPerSkim == "-1":

    options.nFilesPerSkim = len(fileList)

nCycles = len(fileList)/int(options.nFilesPerSkim)

if nCycles*int(options.nFilesPerSkim) < len(fileList):

    nCycles=nCycles+1
    
if int(options.nWorkers) > int(nCycles):
    options.nWorkers = str(nCycles)

log.output("* Number of files to be skimmed: "+str(len(fileList)))
log.output("* Number of files grouped per skim: "+str(options.nFilesPerSkim))
log.output("* Number of TopSkim instances needed: "+str(nCycles))
log.output("* The skimming will be done with "+str(options.nWorkers)+" threads.")

time.sleep(5)

if (debug):
     print "* Number of files to be skimmed: "+str(len(fileList))
     print "* Number of files grouped per skim: "+str(options.nFilesPerSkim)
     print "* Number of TopSkim instances needed: "+str(nCycles)
     print "* The skimming will be done with "+str(options.nWorkers)+" threads."


#nCycles = 2

# first we compile the skimmer

if (debug):
    print "DEBUG: compiling skimmer"

compile = SkimTopTree(0,0,[])

compile.CompileSkimmer()

if (debug1):
    print "DEBUG: compiled skimmer"

# if we need to stageout to pbs let's check if the destination exists

#sys.exit(0)

if (debug1):
    print "DEBUG: checking pbs setup"

if not options.publishName == "NONE":

    if (debug1):
        print "DEBUG: publish name setup"

    log.output("* PNFS Stage-Out option ENABLED, setting up PNFS destination\n")
    if (debug1):
        print "DEBUG: checking pnfs"

    pnfsBase = "/pnfs/iihe/cms/store/user/"+PNFSUserName+"/"+storage_dest+"/"
    
    dest = pnfsBase+options.publishName+"/"+timestamp+"/"
    destination = dest
            
    if not os.path.exists(pnfsBase):
        if (debug1):
            print "DEBUG: creating pnfs directory"  
            if os.path.exists(pnfsBase):
                print "DEBUG: pnfs directory created  " + str(pnfsBase)  
              
        log.output("-> Creating PNFS directory: "+pnfsBase)

        log.output(Popen('srmmkdir '+srm+pnfsBase, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip())

    if not os.path.exists(pnfsBase+options.publishName+"/"):
        if (debug1):
            print "DEBUG: creating timestamped pnfs directory"  

            log.output("-> Creating PNFS directory: "+pnfsBase+options.publishName+"/")

            log.output(Popen('srmmkdir '+srm+pnfsBase+options.publishName+"/", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip())

    if not os.path.exists(dest):

        log.output("-> Creating PNFS directory: "+dest)
        
        log.output(Popen('srmmkdir '+srm+dest, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip())

    if not os.path.exists(dest+"/skim.xml"):

        log.output("-> Copying the skim XML file to: "+dest)
                
        cmd = 'srmcp file:////'+TopSkimDir+"/"+options.xml+" "+srm+dest+"/skim.xml"
                
        log.output(Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip())

# Create our Queue to store TopSkims:

skimPool = Queue.Queue ( 0 )

# Prepare the Skim Threads

#nCycles = 1

if (debug1):
    print "DEBUG: preparing SKIM"

for i in xrange(nCycles):

    filesToSkim=[]

    startIndex = i*int(options.nFilesPerSkim)
    endIndex = startIndex+int(options.nFilesPerSkim)-1

    if not endIndex < len(fileList):

        endIndex = len(fileList)-1

    #print str(startIndex)+" "+str(endIndex)

    for j in range (startIndex,endIndex+1):

        filesToSkim.append(fileList[j])

        #print filesToSkim[j-1]

    #sys.exit(0)

    # create SkimTopTree object
    if (debug1):
        print "DEBUG: invoking the skimmer workhorse"

    skim = SkimTopTree(nSkim,i,filesToSkim)

    if (debug1):
        print "DEBUG: Putting Skim"

    skimPool.put(skim)

    nSkim = nSkim + 1

# announce that this production will be started

if (not options.publishName == "NONE" and options.announce) or options.mtop:
    
    if (debug):
        print "DEBUG: announicing"

    log.output("-> Sending production announcement for this skim")

    #user =  Popen('echo $USER', shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip()
    
    mail = MailHandler(options.email)
    
    message = "Hi,\n\nThis is an automatic email to notify you that user "+PNFSUserName+" is performing a TopTree Skim and requested it to be announced.\n\n\tSource TopTree: "

    for path in options.location.split(","):
        message = message+"\n\t\t"+path

    if options.mtop:
        message = message+"\n\nYou can track the progress of this skim on https://mtop.iihe.ac.be/TopDB/toptrees/getlog/"+str(timestamp)
    message=message+"\n\n An email will be sent upon completion\n\n The following configuration will be used:\n"
    
    for line in open(options.xml,"r"):
        
        message += "\n"+line.strip()

    try:
    
        mail.sendMail("TopTree Skim started by "+PNFSUserName,message)
           
    except:
        
        log.output(" --> UNABLE TO SEND EMAIL. MAYBE VUB SMTP SERVER DOWN AGAIN :@")


# start our threads

workers = []
for x in xrange ( int(options.nWorkers) ):
   workers.append(WorkFlow(x))
   workers[x].start()

# check if there is a worker that are not done

notDone=bool(True)

while notDone:

    notDone = False

    for worker in workers:
    
        if worker.isAlive(): # If there is one worker alive, we are still not finished
            
            notDone=bool(True)
            

    if not notDone:

        log.output("-> All Skims are DONE")

        # remove the temp skimmer dir which we used to compile
        
        Popen("rm -vfr "+skimmerDir_base, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read()

        try:
            perc = round((float(nOutput)/float(nInput))*100,2)
        except:
            perc = 0
    
        log.output("-> Stats: "+str(nOutput)+"/"+str(nInput)+" ("+str(perc)+"%) of the input events where selected.\n")

        if not options.publishName == "NONE":

            srm = "srm://maite.iihe.ac.be:8443"

            stats = open(TopSkimDir+"/stats_"+timestamp+".txt","w")

            stats.write("Stats: "+str(nOutput)+"/"+str(nInput)+" ("+str(perc)+"%) of the input events where selected.\n")

            stats.close()

            if not os.path.exists(destination+"/stats.txt"):

                log.output("-> Transfering the stats file to: "+destination)
                
                cmd = 'srmcp file:////'+TopSkimDir+"/stats_"+timestamp+".txt "+srm+destination+"/stats.txt"
                
                print Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip()

            if os.path.exists(TopSkimDir+"/stats_"+timestamp+".txt"):

                os.remove(TopSkimDir+"/stats_"+timestamp+".txt")
                                     
        if (not options.publishName == "NONE" and options.announce) or options.mtop:
    
            log.output("-> Sending announcement for this skim")

            #user =  Popen('echo $USER', shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip()
    
            mail = MailHandler(options.email)

            message = ""

            if not nFailedJobs == 0:
                message = "-- ERROR -- "+str(nFailedJobs)+" job(s) NOT successful!!!!!!! USE THIS AT YOUR OWN RISK!!!!!\n\n"

            message += "Hi,\n\nThis is an automatic email to notify you that user "+PNFSUserName+" performed a TopTree Skim and requested it to be announced.\n\n\tSource TopTree: "

            for path in options.location.split(","):
                message = message+"\n\t\t"+path

            message = message+"\n\n\tStats: "+str(nOutput)+"/"+str(nInput)+" ("+str(perc)+"%) of the input events where selected.\n\nPlease find your Skimmed TopTree on\n\n"
            
            if not options.mtop:
                message += "\t"+destination
            elif options.mtop and not options.publishName == "NONE":
                message += "\t"+destination
            elif options.mtop:
                message += url
                message += "\nYou can download these files trough your local internet browser or download them on any linux server by using wget --no-check-certificate <URL>"
                message += "\n\nPlease note that this TopTree will be removed from the system within 20 hours.\n\nCheers,\nTopDB"
            
            message += "\n\nDump of the TopSkim configuration used:\n"
    
            for line in open(options.xml,"r"):
        
                message += "\n"+line.strip()

            try:
    
                mail.sendMail("TopTree Skim completed by "+PNFSUserName,message)

            except:

                log.output(" --> UNABLE TO SEND EMAIL. MAYBE VUB SMTP SERVER DOWN AGAIN :@")
                    
                
    time.sleep(5)

if os.path.exists("/localgrid/"+userName+"/grid-proxy_"+timestamp):

    os.remove("/localgrid/"+userName+"/grid-proxy_"+timestamp)


if options.mtop and os.path.exists(options.xml):

    os.remove(options.xml)

    log.output("-> Closing log-file, script out! See ya!!!")

os.rename("logs/log_"+timestamp+".txt","logs/FINISHED_log_"+timestamp+".txt")

try:
    
    for i in xrange(int(options.nWorkers)):
        os.rename("logs/log_"+timestamp+"_thread"+str(i)+".txt","logs/FINISHED_log_"+timestamp+"_thread"+str(i)+".txt")
except:

    print ""
