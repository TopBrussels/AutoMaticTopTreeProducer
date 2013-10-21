# Class to handle the email messages

import time
from time import strftime,gmtime
from datetime import datetime

# interacting with the os
from subprocess import Popen, PIPE, STDOUT

# importing smtp lib
import sys, smtplib

class MailHandler:

    def __init__(self):

        self.smtpServer = "mach.vub.ac.be"

        self.senderAddress = "toptreeproducer@mtop.iihe.ac.be"

        self.toAnnounce = [ "top-brussels-datasets@cern.ch" ]

        self.toError = [ "top-brussels-datasets-admin@cern.ch" ]


    def sendMail(self,type,subject,msg):

        toAddrs = ""
        
        if type == "announcement":
            for to in range(0,len(self.toAnnounce)):
                toAddrs = toAddrs+self.toAnnounce[to]+", "

        if type == "error":
            for to in range(0,len(self.toError)):
                toAddrs = toAddrs+self.toError[to]+", "

        m = "From: %s\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (self.senderAddress, toAddrs, subject)

        try:
            server = smtplib.SMTP(self.smtpServer)
            server.sendmail(self.senderAddress, toAddrs.split(), m+msg)
            server.quit()
        except:
            print "error sending email"

#mail = MailHandler()

#mail.sendMail("error","errorrr","jaja")
