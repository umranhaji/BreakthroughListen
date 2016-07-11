import numpy as np
import fnmatch
import os
import random
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz
from scipy.integrate import simps
from filterbank import Filterbank


#~~~~~~~~~~Global Variables~~~~~~~~~~

GreenBank = EarthLocation(lat=38.4322*u.deg, lon=-79.8398*u.deg) #Western longitudes are negative
fmin = 1350
fmax = 1450

#~~~~~~~~~~Functions~~~~~~~~~~

def shuffler(list): #Shuffles a list (makes random.shuffle act like a conventional function)
    random.shuffle(list)
    return list


def AA(file): #Returns AltAz coords for given observation

    fil = Filterbank(file)
    MJD = fil.header['tstart']
    ra = fil.header['src_raj']
    dec = fil.header['src_dej']

    target = SkyCoord(ra, dec)
    altaz = target.transform_to(AltAz(location=GreenBank, obstime=Time(MJD, format='mjd')))
    dict = { 'alt' : altaz.alt.degree, 'az' : altaz.az.degree }

    return dict


def totalpower(file, fmin, fmax):
    fil = Filterbank(file)
    maxfreq = fil.header['fch1']
    nchans = fil.header['nchans']
    ch_bandwidth = fil.header['foff']
    minfreq = maxfreq + nchans*ch_bandwidth
    if fmin < minfreq or fmax > maxfreq:
        raise ValueError("One of the freq constraints is out of the freq range of this filterbank file.")

    freqs = np.array(fil.freqs)
    data = np.array(fil.data[0][0])

    newfreqs = np.array([x for x in freqs if x >= fmin and x <= fmax])
    idx = np.where(np.in1d(freqs, newfreqs))[0] #Indices of where newfreqs values occur in freqs
    newdata = data[idx]

    totalpower = simps(x=newfreqs, y=newdata)

    return totalpower

#~~~~~~~~~~Main Code~~~~~~~~~~


prompt = True
while prompt:
    sample_size = raw_input("Choose a sample size: ")
    try:
        sample_size=int(sample_size)
        prompt = False
    except:
        print("Not an integer!")
sample_size = int(sample_size)

paths = ['/mnt_blc00', '/mnt_blc01', '/mnt_blc02', '/mnt_blc03', '/mnt_blc04', '/mnt_blc05', '/mnt_blc06', '/mnt_blc07']
files = []

print "Finding filterbank files..."

for path in paths:
    for root, dirs, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*guppi*HIP*gpuspec.0002.fil'):
            files.append(os.path.join(root, filename))

print "Obtaining random sample of {0} files..." .format(sample_size)

files = shuffler(files)
sample  = random.sample(files, sample_size)

alts = []
azs = []
for file in sample:
    alts.append(AA(file)['alt'])
    azs.append(AA(file)['az'])

print alts
print azs
