import cPickle as pickle
from filterbank import Filterbank
import re, os, fnmatch, csv
import numpy as np

#~~~~~~~~~~Functions~~~~~~~~~~

def blc_finder(filename): #Extracts blc number from filterbank filename
    try:
        blc = re.search('blc(\d\d)_guppi', filename).group(1)
        return blc
    except:
        raise ValueError("{0} has inappropriate filename, could not extract blc number." .format(filename))

def HIP_finder(filename): #Obtains HIP number of target star from filterbank filename
    try:
        star = re.search('_HIP(.+?)_', filename).group(1)
        return star
    except:
        raise ValueError("{0} has inappropriate filename, could not extract HIP number." .format(filename))

def spectype(HIPnumber): #Gets two-digit (letter+num) spectral type for given HIP number. Returns letter spectral type if no number available
    with open('/datax2/filterbank_plots/spectral_type_comparer/HYG-Database/hygdata_v3.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['hip'] == HIPnumber:
                if len(row['spect']) >=2 and row['spect'][0].isalpha() and row['spect'][1].isdigit(): #Check if spect is of form "(letter)(number)"
                    return row['spect'][:2]
                elif len(row) == 1 and row['spect'][0].isalpha(): #Check if spect is a one-letter string
                    return row['spect'][0]
                break
    
def maxfreq(file): #Returns max frequency in a .fil file
    fil = Filterbank(file)
    return fil.header['fch1']

def rescode(filename): #Extracts resolution code (0001, 0002, etc.) from filterbank filename
    try:
        rescode = re.search('.gpuspec.(.+?).fil', filename).group(1)
        return rescode
    except:
        raise ValueError("{0} has inappropriate filename, could not extract resolution code." .format(filename))

def keyfinder(file): #Returns key that corresponds to file list in dictionary
    key = "{0}_{1}_{2}" .format(spectype(HIP_finder(file)), rescode(file), maxfreq(file))
    return key

#~~~~~~~~~~Main Code~~~~~~~~~~

print "Finding all HIP filterbank files..."

paths = ['/mnt_blc00', '/mnt_blc01', '/mnt_blc02', '/mnt_blc03', '/mnt_blc04', '/mnt_blc05', '/mnt_blc06', '/mnt_blc07']
files = []
for path in paths:
    for root, dirs, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, 'blc??*guppi*HIP*gpuspec.0002.fil'):
            files.append(os.path.join(root, filename))

print "Categorizing files by paramaters..."

d = {}

for i in range(10):
#for file in files:
    file = files[i]
    count = len(d)

    print "Number of Keys = {0}" .format(count)
    print "Files left to search = {0}" .format(len(files))

    if spectype(HIP_finder(file)) is None:
        print "No vaiid spectype found for {0}" .format(file)
    else:
        key = keyfinder(file)
        if key in d:
            print "{0} already in dict. Adding file." .format(key)
            if not file in d[key]:
                d[key].append(file)
            else:
                print "File already in dict value. Skipping..."
        if not key in d:
            d[key] = []
            d[key].append(file)
            print "Added {0} to dict" .format(key)

    files.remove(file)

for key, value in d.items():
    print (key, '---->', value)

print
print "Saving dictionary to pickle file..."

with open('spectype_configurations.pkl', 'wb') as picklefile:
    pickle.dump(d, picklefile)
