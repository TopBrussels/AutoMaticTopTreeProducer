# Class for parsing the framework jobreport XML files
from xml.sax.handler import ContentHandler

class FJRHandler(ContentHandler):
	
        # constructor
        def __init__ (self):

                # is the current element one of the interesting ones
                self.isFrameworkErrorElement = 0
		self.isPFNElement = 0
		self.isEventElement = 0
		self.isEventsReadElement = 0
                # record the value of interesting attributes
		self.frameworkExitStatus = "-9999"
                self.frameworkError = ''
		self.lastPFN = ''
		self.TotalEvents = 0
		self.EventsRead = 0
		self.foundWrapperExit=0

        # this is called for each element
        def startElement(self, name, attrs):
                if name == 'FrameworkError':
	               	attrName = attrs.get('Type')
                        if attrName == 'CMSException':
				self.frameworkError = ''
	                        self.isFrameworkErrorElement = 1
			if attrName == 'WrapperExitCode':
				self.frameworkExitStatus = attrs.get('ExitStatus')
				
		if name == 'PFN' and attrs.get('Value') != "None" :
				self.lastPFN = ''
				self.isPFNElement = 1

		if name == 'TotalEvents':
			#self.TotalEvents =
			#print name
			self.isEventElement = 1

		if name == 'EventsRead' and self.TotalEvents == 0:

			self.isEventsReadElement = 1


        def characters (self, ch):
                if self.isFrameworkErrorElement == 1:
                        self.frameworkError += ch.lstrip('\t')
			
		if self.isPFNElement == 1:
			if ch.endswith('.root'):
				self.lastPFN = ch.lstrip('\t')

		if self.isEventElement == 1:
			
			#self.TotalEvents += ch.lstrip('\n\t')

			try:
				self.TotalEvents = int(ch.lstrip('\n\t'))

			except:
				pass
			
		if self.isEventsReadElement == 1:

			#self.EventsRead += int(ch.lstrip('\n\t'))

			try:
				self.EventsRead += int(ch.lstrip('\n\t'))

			except:
				pass

        # this is called when an element is closed
        def endElement(self, name):
                # this is an attribute of some kind
                if name == 'FrameworkError' and self.isFrameworkErrorElement:
                        self.isFrameworkErrorElement = 0
			
		if name == 'PFN' and self.isPFNElement:
                        self.isPFNElement = 0

		if name == 'TotalEvents' and self.isEventElement:
			self.isEventElement = 0

		if name == 'EventsRead' and self.isEventsReadElement:
			self.isEventsReadElement = 0
	

	def getFrameworkError(self):
		return 'Last input file that was successfully opened: '+self.lastPFN+'\n'+self.frameworkError

	def getFrameworkExitCode(self):
		return self.frameworkExitStatus

	def getEventsProcessed(self):
		if not self.TotalEvents == 0:

			return self.TotalEvents

		else:

			return self.EventsRead


# Class for parsing the framework jobreport XML files
from xml.sax.handler import ContentHandler

class GreenBoxHandler(ContentHandler):
	
        # constructor
        def __init__ (self):

                # is the current element one of the interesting ones
                self.isGoodElement = 0
		
                # record the value of interesting attributes
		self.Availability = 0
		
        # this is called for each element
        def startElement(self, name, attrs):

		if name == 'availability':

			self.Availability = 0
			self.isGoodElement = 1
		

        def characters (self, ch):
                if self.isGoodElement == 1:
                        self.Availability += int(ch.lstrip('\t'))
			
		
        # this is called when an element is closed
        def endElement(self, name):
                # this is an attribute of some kind
                if name == 'availability' and self.isGoodElement:
                        self.isGoodElement = 0
	

	def getAvailability (self):

		return self.Availability


