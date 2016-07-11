from filterbank import Filterbank
import numpy as np
import os
import fnmatch
import random
import re
import csv
import argparse


parser = argparse.ArgumentParser(description='Extract params from fils')
parser.add_argument('filename', type=str, help='Path to fil file')
args = parser.parse_args()
filename = args.filename


#~~~~~~~~~~Functions~~~~~~~~~~


def band(file): #Classifies filterbank file into a band according to its middle freq
    fil = Filterbank(file)
    fmax = fil.header['fch1']
    nchans = fil.header['nchans']
    ch_bandwidth = fil.header['foff']
    fmid = fmax + (nchans*ch_bandwidth)/2.0

    if 1000 <= fmid < 2000:
        band = 'L'
    elif 2000 <= fmid < 4000:
        band = 'S'
    elif 4000 <= fmid < 8000:
        band = 'C'
    elif 8000 <= fmid < 12000:
        band = 'X'
    return band


def blc(filename): #Extracts blc number from filterbank filename
    try:
        blc = re.search('blc(.+?)_', filename).group(1)
        return blc
    except:
        raise ValueError("{0} has inappropriate filename, could not extract blc number." .format(filename))


def shuffler(list): #Shuffles list (makes random.shuffle act like a conventional function)
    random.shuffle(list)
    return list
            
def HIP(filename): #Obtains Hipparcos number of target star from filterbank filename
    try:
        star = re.search('HIP(.+?)_', filename)
        return star
    except:
        raise ValueError("{0} does not have appropriate filename, could not extract HIP number." .format(filename))

def spectype(HIPnumber): #Gets spectral type for given HIP number
    with open('hygdata_v3.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['hip'] == {0} .format(HIPnumber):
                return row['spect']

#~~~~~~~~~~Main Code~~~~~~~~~~


prompt = True
while prompt:
    sample_size = raw_input("Choose a sample size: ")
    try:
        sample_size = int(sample_size)
        prompt = False
    except:
        print 'Not an integer!'

blc = blc(filename)
path = '/mnt_blc{0}' .format(blc)

print "Finding filterbank files..."

files = []
for root, dirs, filenames in os.walk(path):
    for filename in fnmatch.filter(filenames, 'blc{}*guppi*HIP*gpuspec.0002.fil' .format(blc)):
        files.append(os.path.join(root, filename))

files = shuffler(files)

print "Building sample of {0} files..."

sample = []
while len(sample) < sample_size:
    newfile = random.choice(files)
    if 


