#!/bin/bash

dir="$1/src/ConfigurationFiles"

rm -v toremove

find $dir -name *.stderr >> toremove
find $dir -name *.stdout >> toremove
find $dir -name *.xml >> toremove
find $dir -name out*.tgz >> toremove

for i in $(cat toremove); do

  rm -v $i

done

rm -v toremove
