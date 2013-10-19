#!/bin/bash

# Script created by doHeartBeat.py that sleeps for ten minutes

outFile=output.txt

if [ -f $outFile ]; then

	# outFile exists already, so remove it!
	rm $outFile

fi

beginTime=`date -u '+%d%m%Y_%H%M%S'`
echo "Starting Job:  Time=$beginTime " >> $outFile
echo "Sleeping for 600 seconds" >> $outFile
sleep 600
endTime=`date -u '+%d%m%Y_%H%M%S'`
echo "Job ended:  Time=$endTime " >> $outFile
