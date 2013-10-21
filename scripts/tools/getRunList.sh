#!/bin/bash

# Download official JSON file at location $1

rm -rfv JSON.txt

wget -O JSON.txt $1 >& /dev/null

# get runs from JSON

list=$(cat JSON.txt | tr "\":" '\n' | grep -v ',' | grep -v "{")

echo $list

exit

## old code

echo $list | tr ' ' '\n' >> tmp

runlist=$(cat tmp)

nRuns=$(cat tmp | wc -l)

rm -v tmp

echo $nRuns 

counter=0

runs={}

processed=0

for i in $runlist;do

#echo $i

let remain=$nRuns-$processed

    if [ $counter -lt 10 ]; then

	#echo $i
	#echo $counter
	runs[$counter]=$i

	let counter=$counter+1
	
    #elif [ $remain -eq 0 ] && [ $counter -lt 10 ];then

	
	#echo "bla $counter $remain"

    elif [ $counter -eq 10 ] || [ $remain -eq 0 ];then

	counter=0

	echo "${runs[0]},${runs[1]},${runs[2]},${runs[3]},${runs[4]},${runs[5]},${runs[6]},${runs[7]},${runs[8]},${runs[9]}"
echo "Processed $processed runs (remaining $remain)"

    fi

let processed=$processed+1

done

echo "Processed $processed runs"
rm -rf JSON.txt
