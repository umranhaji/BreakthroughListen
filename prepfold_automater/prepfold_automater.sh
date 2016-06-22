#!/bin/bash
source /usr/local/pulsar64/pulsar.csh >& /dev/null

totalPSRfils=$(find /mnt_blc??/datax*/ -name "*guppi*gpuspec.8.0001.fil" | wc -w)
totalpfd=$(find /datax2/prepfold_outputs/ -name "*.pfd" | wc -w)
totaldifference=$(($totalPSRfils - $totalpfd))

echo ""
echo "This script will search for pulsar filterbank files of the format
*guppi*gpuspec.8.0001.fil for a given date range and run prepfold on them,
outputting the products in /datax2/prepfold-output/. You can also process
files from al ldates instead of providing a custom data range.

Currently there are a total of $totaldifference pulsar filterbank files
which have not been run through prepfold.
"
read -p "Would you like to provide a date range? (y/n): " choice

for file in /datax2/prepfold_outputs/*.fil
do
    filename=$(echo $(basename "$file"))
    NOFIL=$(echo $filename | sed 's/\(.*\)\.fil/\1/') #Cuts off .fil extension
    PULSAR=$(echo $filename | awk -F_PSR_ '{print $2}' | awk -F_ '{print $1}')

    pfd="${NOFIL}_PSR_${PULSAR}.pfd"

    echo $filename
    echo $NOFIL
    echo $PULSAR
    echo $prepfoldproduct

    

done

