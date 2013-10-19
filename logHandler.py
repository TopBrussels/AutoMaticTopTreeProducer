# this class creates the logFile

# working with time
import time
from time import strftime
from datetime import datetime

# regular expressions
import re

# interacting with the os
import subprocess
from subprocess import Popen, PIPE, STDOUT

# for getting stuff from fjr files
from fjrHandler import FJRHandler
from xml.sax import make_parser 

# handling email

from MailHandler import MailHandler

import os, os.path

import sys

class logHandler:

    def __init__ (self,fileName):

	self.logFile = fileName

        self.dataset = ""

        self.sendErrorMails = bool(False)

        if not self.logFile == "" and os.path.exists(self.logFile):

            os.remove(self.logFile)

        self.announcementMsg = ""

    def setDataSet(self,string):
        self.dataset = string

    def sendErrorMails(self,send):
        self.sendErrorMails = send

    def getLogFileName(self):
	
	return self.logFile

    def appendToMSG(self,string):
        self.announcementMsg=self.announcementMsg+"\n"+string

    def getAnnouncementMSG(self):
        return self.announcementMsg

    def output(self,string):
        
        if not self.logFile == "":

            f = open(self.logFile,"a")

            f.write("\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+string)

            f.write("\n")

	    f.close()

	else:

            print "\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"] "+string

    def outputNoTime(self,string):
        
        if not self.logFile == "":

            f = open(self.logFile,"a")

            f.write("\n"+string)

            f.write("\n")

	    f.close()

	else:

            print "\n"+string


    def analyseFJR(self,file,stdout):

        self.output("\n---> Examining failed job: "+file)

        parser = make_parser()

	if file != '' and file != 'CVS':
		
            # file to write errors to
            #errorLog = open(self.logFile,"a")
            
            # parser for fjr files
            handler = FJRHandler()
            parser.setContentHandler(handler)

            parser.parse(open(file))

            # get error message from fjr and write to error report
            # for this site...

            jobExitCode = handler.getFrameworkExitCode()

            ## EXIT CODE 8001
			
            if int(jobExitCode) == 8001:

                # get the host the job ran on
                cmd ='grep -C 1 \"Today is\" ' + stdout
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                hostNameDate = pExe.stdout.read()
                self.outputNoTime('\n\t\t ***** Job with error 8001 *****\n\n')
                self.outputNoTime(hostNameDate + '\n')
                self.outputNoTime(handler.getFrameworkError())
			
            ## EXIT CODE 8020
		
            elif int(jobExitCode) == 8020:
                
                # get the host the job ran on
                cmd ='grep -C 1 \"Today is\" ' + stdout
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                hostNameDate = pExe.stdout.read()
                self.outputNoTime('\n\t\t ***** Job with error 8020 *****\n\n')
                self.outputNoTime(hostNameDate + '\n')
                self.outputNoTime(handler.getFrameworkError())
                
            ## EXIT CODE 60303

            elif int(jobExitCode) == 60303:
                # get the host the job ran on
                cmd ='grep -C 1 \"Today is\" ' + stdout
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                hostNameDate = pExe.stdout.read()
                self.outputNoTime('\n\t\t ***** Job with error 60303 *****\n\n')
                self.outputNoTime(hostNameDate + '\n')
                #check if the "python cmscp.py" command contains "--debug"
                cmd ='grep -A 2 "Copy output files from WN" ' + stdout + ' | grep "python cmscp.py" | grep "\-\-debug"'
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                hostNameDate = pExe.stdout.read()
                if hostNameDate != '':
                    cmd = 'grep -A 90 \"Copy output files from WN\" ' + stdout
                    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    error = pExe.stdout.read()
                    self.outputNoTime(error + '\n\n')
                else:
                    cmd = 'grep -A 30 \"Copy output files from WN\" ' + stdout
                    pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    error = pExe.stdout.read()
                    self.outputNoTime(error + '\n\n')
                    

                    
            ## EXIT CODE 60307

            elif int(jobExitCode) == 60307:
                    
                # get the host the job ran on
                cmd ='grep -C 1 \"Today is\" ' + stdout
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                hostNameDate = pExe.stdout.read()
                self.outputNoTime('\n\t\t ***** Job with error 60307 *****\n\n')
                self.outputNoTime(hostNameDate + '\n')
                cmd = 'grep -A 50 \"Copy output files from WN\" ' + stdout
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                error = pExe.stdout.read()
                self.outputNoTime(error + '\n\n')
                
                cmd = 'grep \"lcg_cp: Connection timed out\" ' + stdout
                pExe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                if pExe.stdout.read() != '':
                        
                    self.outputNoTime(pExe.stdout.read() + '\n\n')
                        

    def dieOnError(self,string):

        self.output("********** SCRIPT GOT TERMINATE SIGNAL -> ALERTING PRODUCTION TEAM **********")
        
        mail = MailHandler()

        type = "error"

        subject = "AutoMaticTopTreeProducer failed"

        msg = "Dear top quark production group,\n"
        msg += "\n"
        msg += "This is an automatically generated e-mail to inform you that the production of "+self.dataset+" failed."
        msg += "\n\nReason:"
        msg += "\n\n\t"+string
        msg += "\n\nLogfile for this production: "+self.logFile

        msg += "\n\n\nCheers,\nAutoMaticTopTreeProducer.py (killed in combat)"

        if self.sendErrorMails:
            mail.sendMail(type,subject,msg)

        
        sys.exit(2)
