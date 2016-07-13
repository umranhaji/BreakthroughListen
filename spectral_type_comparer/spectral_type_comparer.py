from filterbank import Filterbank
import numpy as np
import matplotlib.pyplot as plt
import os, fnmatch, random, re, csv, argparse


parser = argparse.ArgumentParser(description='Extract params from fils')
parser.add_argument('filename', type=str, help='Path to fil file')
args = parser.parse_args()
filename = args.filename

fil = Filterbank(filename)
source = fil.header['source_name']
file_data = fil.data[0][0]

#~~~~~~~~~~Functions~~~~~~~~~~


def band_finder(filename): #Classifies filterbank file into a band according to its middle freq
    fil = Filterbank(filename)
    fmax = fil.header['fch1']
    nchans = fil.header['nchans']
    ch_bandwidth = fil.header['foff']
    fmid = fmax + (nchans*ch_bandwidth)/2.0
    if 1000 <= fmid < 2000:
        return 'L'
    elif 2000 <= fmid < 4000:
        return 'S'
    elif 4000 <= fmid < 8000:
       return 'C'
    elif 8000 <= fmid < 12000:
        return 'X'

def blc_finder(filename): #Extracts blc number from filterbank filename
    try:
        blc = re.search('blc(\d\d)_guppi', filename).group(1)
        return blc
    except:
        raise ValueError("{0} has inappropriate filename, could not extract blc number." .format(filename))

def rescode(filename): #Extracts resolution code (0001, 0002, etc.) from filterbank filename
    try:
        rescode = re.search('.gpuspec.(.+?).fil', filename).group(1)
        return rescode
    except:
        raise ValueError("{0} has inappropriate filename, could not extract resolution code." .format(filename))

def shuffler(list): #Shuffles list (makes random.shuffle act like a conventional function)
    random.shuffle(list)
    return list

def catalog_finder(filename): #Determines the catalog a star is in
    if "HIP" in filename:
        return "HIP" #Hipparcos
    if "GJ" in filename:
        return "GJ" #Gliese

def starnumber_finder(filename): #Obtains catalog number of target star from filterbank filename
    if catalog_finder(filename) == "HIP":
        try:
            star = re.search('_HIP(.+?)_', filename).group(1)
            return star
        except:
            raise ValueError("{0} has inappropriate filename, could not extract HIP number." .format(filename))
    if catalog_finder(filename) == "GJ":
        try:
            star = re.search('_GJ(.+?)_', filename).group(1)
            return star
        except:
            raise ValueError("{0} has inappropriate filename, could not extract GJ number." .format(filename))

def spectype(catalog, starnumber): #Gets two-digit spectral type given catalog and number
    if catalog == "HIP":
        with open('/datax2/filterbank_plots/spectral_type_comparer/HYG-Database/hygdata_v3.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['hip'] == starnumber:
                    return row['spect'][:2]
                    break
    if catalog == "GJ":
        with open('/datax2/filterbank_plots/spectral_type_comparer/HYG-Database/hygdata_v3.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['gl'] == starnumber:
                    return row['spect'][:2]
                    break

def maxfreq(file): #Returns max frequency in a .fil file
    fil = Filterbank(file)
    maxfreq = fil.header['fch1']
    return maxfreq

def avg_data(files): #Finds mean and median power spectrum profiles given a list of files of same frequency range
    data = []
    for file in files:
        fil = Filterbank(file)
        power_vals = fil.data[0][0]                  
        data.append(power_vals)

    data = np.array(data)
    stacked_data = np.dstack(data)[0] #Turns data into array of length equal to # of chans, each of size equal to number of data points

    mean_data = []
    median_data = []
    for channel in stacked_data:
        mean_data.append(np.mean(channel))
        median_data.append(np.median(channel))

    mean_data=np.array(mean_data)
    median_data=np.array(median_data)
    freqs = np.array(Filterbank(files[0]).freqs)
    dict = { 'freqs':freqs, 'mean_data':mean_data, 'median_data':median_data }
    return dict

        
#~~~~~~~~~~Main Code~~~~~~~~~~

print catalog_finder(filename)
print starnumber_finder(filename)


print "Extracting star and band information from file..."

cat = catalog_finder(filename)
star = starnumber_finder(filename)
spec = spectype(cat, star)
blc = blc_finder(filename)
band = band_finder(filename)
fmax = maxfreq(filename)
res = rescode(filename)

print
print "Star = {0}{1}" .format(cat, star)
print "Spectral Type = {0}" .format(spec)
print "Compute Node = {0}" .format(blc)
print "Band = {0}" .format(band)
print "Max Freq = {0}" .format(fmax)
print "Resolution Code = {0}" .format(res)
print

#Prompt user for sample size:

prompt = True
while prompt:
    sample_size = raw_input("Choose a sample size: ")
    try:
        sample_size = int(sample_size)
        prompt = False
    except:
        print 'Not an integer!'

#Search directories for appropriate filterbank files:

print "Finding filterbank files in compute node {0} with rescode {1}..." .format(blc,res)
print

path = '/mnt_blc{0}' .format(blc)
files = []


for root, dirs, filenames in os.walk(path):
    for filename in fnmatch.filter(filenames, 'blc{0}*guppi*gpuspec.{1}.fil' .format(blc,res)):
        files.append(os.path.join(root, filename))
files = shuffler(files)

print "Building sample of {0} files of same band and spectral type..." .format(sample_size)
print

sample = []
count = 0
while len(sample) < sample_size:
    print "Current sample size = {}" .format(count)
    newfile = random.choice(files)
    files.remove(newfile)
    print "Files left to search = {0}" .format(len(files))
    if spectype(catalog_finder(newfile), starnumber_finder(newfile)) == spec and maxfreq(newfile) == fmax:
        sample.append(newfile)
        count = len(sample)
        print "Added {0} to sample." .format(newfile)
    if len(files) == 0:
        raise RuntimeError("Your chosen sample size is larger than the \
number of compatible files. Please try again with smaller sample size.")

print
print 'Sample construction complete!'
print
print "Finding mean and median profiles..."

freqs = avg_data(sample)['freqs']
mean_data = avg_data(sample)['mean_data']
median_data =  avg_data(sample)['median_data']

mean_resids = file_data - mean_data
median_resids = file_data - median_data

print
print "Plotting..."

plt.figure(1)
plt.subplot(221)
plt.plot(freqs, mean_data)
plt.xlim(freqs[0], freqs[-1])
plt.title("Mean Profile for Type {0}" .format(spec))
plt.xlabel("Frequency [MHz]")
plt.ylabel("Power")
plt.grid()
plt.ticklabel_format(useOffset=False)

plt.subplot(222)
plt.plot(freqs, median_data)
plt.xlim(freqs[0], freqs[-1])
plt.title("Median Profile for Type {0}" .format(spec))
plt.xlabel("Frequency [MHz]")
plt.ylabel("Power")
plt.grid()
plt.ticklabel_format(useOffset=False)

plt.subplot(223)
plt.plot(freqs, mean_resids)
plt.xlim(freqs[0], freqs[-1])
plt.title("{0} Minus Mean {1} Profile" .format(source, spec))
plt.xlabel("Frequency [MHz]")
plt.ylabel("Power")
plt.grid()
plt.ticklabel_format(useOffset=False)

plt.subplot(224)
plt.plot(freqs, median_resids)
plt.xlim(freqs[0], freqs[-1])
plt.title("{0} Minus Median {1} Profile" .format(source, spec))
plt.xlabel("Frequency [MHz]")
plt.ylabel("Power")
plt.grid()
plt.ticklabel_format(useOffset=False)

plt.tight_layout()
plt.show()
