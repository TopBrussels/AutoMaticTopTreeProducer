from logHandler import logHandler
from CrabHandler import CRABHandler

crab = CRABHandler("",".",logHandler(""))

crab.createGridProxy()

crab.createMyProxyCredentials()

#print crab.pickProxy()
