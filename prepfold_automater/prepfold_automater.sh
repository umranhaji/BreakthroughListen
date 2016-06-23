#!/bin/bash

#source /usr/local/pulsar64/pulsar.csh >& /dev/null

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

if [ "$choice" = "n" ]; then

    echo ""
    echo "Running prepfold on all pulsar filterbank files..."

    sleep 3s

    for file in $(find /mnt_blc??/datax*/ -name "*guppi*gpuspec.8.0001.fil"); do 

	status=$(cat /home/obs/triggers/observation_status)
	if [ "$status" != "off" ]; then
	    echo ""
	    echo "Observations in progress. Terminating plot generation."
	    exit
	fi

	filename=$(echo $(basename "$file"))
	NOFIL=$(echo $filename | sed 's/\(.*\)\.fil/\1/') #Cuts off .fil extension
	PULSAR=$(echo $filename | awk -F_PSR_ '{print $2}' | awk -F_ '{print $1}')
	pfd="/datax2/prepfold_output/${NOFIL}_PSR_${PULSAR}.pfd"

	if test -e $pfd; #Checks if one of the outputs of prepfold corresponding to the .fil file already exists in directory.
	    then echo "Prepfold products for $filename already exists in /datax2/prepfold_output/. Skipping..."
	    else
	         echo "Running prepfold on $filename..."
		 cp $file /datax2/prepfold_output
		 csh /home/obs/bin/prepfold_wrapper /datax2/prepfold_output/"${filename}"
		 rm /datax2/prepfold_output/"${filename}"
	    fi
    done

echo ""
echo "All plots complete."
fi

if [ "$choice" = "y" ]; then

    read -p "Please enter the Modified Julian Date (MJD) that you would like to start at: " MJDstart
    read -p "Now enter the MJD that you would like to stop at: " MJDstop
    echo "Finding pulsar .fil files for observations in given date range..."

    sleep 3s

    for i in $(seq $MJDstart $MJDstop); do
	numberfils=$(find /mnt_blc??/datax*/ -name "*guppi_${i}_*gpuspec.8.0001.fil" | wc -w)
	numberPFD=$(find /datax2/prepfold_output/ -name "*guppi_${i}_*.pfd" | wc -w)
	difference=$(($numberfils - $numberPFD))
	arraydifferences+=($difference)
    done	

    for i in ${arraydifferences[@]}; do
	totaldifferences=$(expr $totaldifferences + $i)
    done

    echo ""
    echo "Currently there are $totaldifferences pulsar .fil files in this date
range whose prepfold products have not been produced."
    sleep 3s
    echo ""
    echo "Running prepfold on pulsar .fil files in this date range..."
    sleep 2s

    for i in $(seq $MJdstart $MJDstop); do
	for file in $(find /mnt_blc??/datax*/ -name "*guppi_${i}_*gpuspec.8.0001.fil"); do

	    status=$(cat /home/obs/triggers/observation_status)
            if [ "$status" != "off" ]; then
		echo ""
		echo "Observations in progress. Terminating plot generation."
		exit
            fi
	   
	    filename=$(echo $(basename "$file"))
	    NOFIL=$(echo $filename | sed 's/\(.*\)\.fil/\1/') #Cuts off .fil extension
	    PULSAR=$(echo $filename | awk -F_PSR_ '{print $2}' | awk -F_ '{print $1}')
	    pfd="/datax2/prepfold_output/${NOFIL}_PSR_${PULSAR}.pfd"

	    if test -e $pfd; #Checks if one of the outputs of prepfold corresponding to the .fil file already exists in directory.
            then echo "Prepfold products for $filename already exists in /datax2/prepfold_output/. Skipping..."
            else
                 echo "Running prepfold on $filename..."
                 cp $file /datax2/prepfold_output
                 csh /home/obs/bin/prepfold_wrapper /datax2/prepfold_output/"${filename}"
                 rm /datax2/prepfold_output/"${filename}"
            fi
	done
    done

    echo ""
    echo "Prepfold complete for MJD range ${MJDstart} to ${MJDstop}."
    
fi


