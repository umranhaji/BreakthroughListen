import numpy as np
import fnmatch, os, random, math
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz
from scipy.integrate import simps
from scipy.interpolate import Rbf, griddata
from filterbank import Filterbank
from matplotlib.pyplot import *

#~~~~~~~~~~Global Variables~~~~~~~~~~

GreenBank = EarthLocation(lat=38.4322*u.deg, lon=-79.8398*u.deg) #Western longitudes are negative
fmin = 1350
fmax = 1450
fch1 = 1501.463

#~~~~~~~~~~Functions~~~~~~~~~~

def shuffler(list): #Shuffles a list (makes random.shuffle act like a conventional function)
    random.shuffle(list)
    return list

def maxfreq(file):
    fil = Filterbank(file)
    maxfreq = float(fil.header['fch1'])
    return maxfreq

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

#def plot_polar_contour(alts, azs, powers):
#    radii = np.cos(np.radians(alts))
#    theta = np.radians(azs)

#    radii, theta = np.meshgrid(radii, theta)

#    fig, ax = subplots(subplot_kw=dict(projection='polar'))
#    ax.set_theta_zero_location("N")
#    ax.set_theta_direction(-1)
#    autumn()
#    cax=ax.contourf(theta, radii, powers, 30)
#    autumn()
#    cb = fig.colorbar(cax)
#    cb.set_label('label')

#    return fig, ax, cax



#~~~~~~~~~~Main Code~~~~~~~~~~


prompt = True
while prompt:
    sample_size = raw_input("Choose a sample size: ")
    try:
        sample_size=int(sample_size)
        prompt = False
    except:
        print("Not an integer!")

#paths = ['/mnt_blc00', '/mnt_blc01', '/mnt_blc02', '/mnt_blc03', '/mnt_blc04', '/mnt_blc05', '/mnt_blc06', '/mnt_blc07']
files = []

print
print "Finding filterbank files..."

for root, dirs, filenames in os.walk('/mnt_blc04'):
    for filename in fnmatch.filter(filenames, '*guppi*HIP*gpuspec.0002.fil'):
        files.append(os.path.join(root, filename))

print
print "Obtaining random sample of {0} files..." .format(sample_size)

files = shuffler(files)

sample = []
count = 0
while len(sample) < sample_size:
    print "Current sample size = {0}" .format(count)
    newfile = random.choice(files)
    files.remove(newfile)
    print "Files left to search = {0}" .format(len(files))
    if np.round(maxfreq(newfile), decimals=3) == fch1:
        sample.append(newfile)
        count = len(sample)
        print "Add {0} to sample." .format(newfile)
    if len(files) == 0:
        raise RuntimeError("Your chosen sample size is larger than the number of compatible files. Please try again with a smaller sample size.")

print
print "Calculating alt, az, and power values..."

alts = []
azs = []
powers =[]
for file in sample:
    alts.append(AA(file)['alt'])
    azs.append(AA(file)['az'])
    powers.append(totalpower(file,1350,1450))
    print "Calculated values for {0} files." .format(len(alts))

alts = np.array(alts)
azs = np.array(azs)
powers = np.array(powers)

import matplotlib.pyplot as plt

print "Plotting..."

x = azs
y = alts
z = powers
xi, yi = np.linspace(0, 360, 360), np.linspace(0, 90, 90)
xi, yi = np.meshgrid(xi, yi)
rbf = Rbf(x,y,z, function='linear')

#zi = griddata((x,y), z, (xi,yi), method='cubic')

zi = rbf(xi,yi)

plt.imshow(zi, vmin=z.min(), vmax=z.max(), origin='lower', extent=[0,360,0,90], aspect='auto')
plt.colorbar()
plt.scatter(x,y,c=z)
plt.title("Total Power from {0} to {1} MHz" .format(fmin, fmax))
plt.xlabel("Azimuth of Observation (degrees)")
plt.ylabel("Altitude of Observation (degrees)")
plt.show()




