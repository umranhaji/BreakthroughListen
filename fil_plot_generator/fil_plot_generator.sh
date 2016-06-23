#!/bin/bash

totalfils=$(find /mnt_blc??/datax*/ -name "*_guppi_*gpuspec.000?.fil" | wc -w)
totalplots=$(find /datax2/filterbank_plots/ -name "*.png" | wc -w)
difference=$(($totalfils - $totalplots))

echo ""
echo "This script will search for filterbank files of the format 
"'*_guppi_*gpuspec.000?.fil'" for a given date range and generate 
.png power spectrum plots of them using filterbank.py. You can
also process files from all dates instead of providing a custom date range. 

Currently there are a total of $difference filterbank files whose
plots have not yet been produced.
"
read -p "Would you like to provide a date range? (y/n): " choice

if [ "$choice" = "n" ]; then
    
   echo ""
   echo "Producing plots for all .fil files..."
    
   sleep 3s

   echo "The following files caused errors in filterbank.py:" > /datax2/filterbank_plots/badfils.txt

   for file in $(find /mnt_blc??/datax*/ -name "*_guppi_*gpuspec.000?.fil"); 
   do

        status=$(cat /home/obs/triggers/observation_status)
	if [ "$status" != "off" ]; then
	    echo "Observations in progress. Terminating plot generation."
	    exit
	fi

	filename=$(echo $(basename "$file"))
	NOFIL=$(echo $filename | sed 's/\(.*\)\.fil/\1/') #Cuts off the .fil extension
	plotpath="/datax2/filterbank_plots/${NOFIL}.png"

	if test -e "$plotpath"; #Checks if the .png plot corresponding to the .fil file already exists in directory.
	     then echo "PNG plot for ${filename} already exists in filterbank_plots. Skipping..."
	     else 
	          echo "Commencing plot generation for ${filename}..."
		  cp $file /datax2/filterbank_plots
		  python /datax2/filterbank_plots/filterbank_noshowplot.py -s "${NOFIL}.png" $file
		     if [ $? -ne 0 ]; then 
			 echo $file >> /datax2/filterbank_plots/badfils.txt
		     fi
		  rm /datax2/filterbank_plots/"${filename}"

	fi
   done

echo ""
echo "All plots complete."
fi 

if [ "$choice" = "y" ]; then

   read -p "Please enter the Modified Julian Date (MJD) that you would like to start at: " MJDstart
   read -p "Now enter the MJD the you would like to stop at: " MJDstop
   echo "Finding .fil files for observations in given date range..."

   sleep 3s

   for i in $(seq $MJDstart $MJDstop)
   do
       numberfils=$(find /mnt_blc??/datax*/ -name "*_guppi_${i}_*gpuspec.000?.fil" | wc -w)
       numberplots=$(find /datax2/filterbank_plots/ -name "*_guppi_${i}_*gpuspec.000?.png" |wc -w)
       difference=$(($numberfils - $numberplots))
       arraydifferences+=($difference) 
   done

   for i in ${arraydifferences[@]}
   do
       totaldifferences=$(expr $totaldifferences + $i)
   done

   echo ""
   echo "Currently there are $totaldifferences filterbank files in this 
date range whose plots have not been produced."
   sleep 3s
   echo ""
   echo "Beginning plot generation for this date range..."
   sleep 2s
   
   for i in $(seq $MJDstart $MJDstop)
   do
      for file in $(find /mnt_blc??/datax*/ -name "*_guppi_${i}_*gpuspec.000?.fil"); 
      do

	status=$(cat /home/obs/triggers/observation_status)
	if [ "$status" != "off" ]; then
	    echo "Observations in progress. Terminating plot generation."
	    exit
	fi

         filename=$(echo $(basename "$file"))
	 NOFIL=$(echo $filename | sed 's/\(.*\)\.fil/\1/') #Cuts off the .fil extension
	 plotpath="/datax2/filterbank_plots/${NOFIL}.png"


	 if test -e "$plotpath"; #Checks if the .png plot corresponding to the .fil file already exists in directory.
	     then echo "PNG plot for ${filename} already exists in filterbank_plots. Skipping..."
	     else 
	          echo "Commencing plot generation for ${filename}..."
		  cp $file /datax2/filterbank_plots
		  python /datax2/filterbank_plots/filterbank_noshowplot.py -s "${NOFIL}.png" $file
		  rm /datax2/filterbank_plots/"${filename}"
	 fi
      done

      echo ""
      echo "Plots complete for MJD range ${MJDstart} to ${MJDstop}."

   done
fi