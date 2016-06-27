import subprocess
import argparse

#This script takes in a .fil file and uses the SIGPROC header function to return various parameters of it.
parser = argparse.ArgumentParser(description='Extract parameters from .fil files')
parser.add_argument('filename', type=str, help='Path to .fil file to be read')
args = parser.parse_args()
filename = args.filename

def band_classifier(x): #Uses 'x', the middle frequency of the spectrum, to determine the band
    #x must be in MHz!
    if 1000 <= x < 2000:
        band = 'L'
    elif 2000 <= x < 4000:
        band = 'S'
    elif 4000 <= x < 8000:
        band = 'C'
    elif 8000 <= x < 12000:
        band = 'X'
    elif 12000 <= x < 18000:
        band = 'Ku'
    elif 18000 <= x < 27000:
        band = 'K'
    return band

def params(filename):
   
    fmax=subprocess.Popen(['/usr/local/sigproc/bin/header', filename, '-fch1'], stdout=subprocess.PIPE) #Obtains freq (MHz) of first channel from SIGPROC header function
    fmax=float((fmax.communicate()[0]))
    
    nchans=subprocess.Popen(['/usr/local/sigproc/bin/header', filename, '-nchans'], stdout=subprocess.PIPE) #Number of channels, from SIGPROC header
    nchans=float(nchans.communicate()[0])

    ch_bandwidth=subprocess.Popen(['/usr/local/sigproc/bin/header', filename, '-foff'], stdout=subprocess.PIPE) #Channel bandwitch, from SIGPROC header
    ch_bandwidth=float(ch_bandwidth.communicate()[0]) 

    bandwidth = (nchans)*(ch_bandwidth) #Bandwidth of the entire spectrum from the .fil file
    fmin = fmax + bandwidth

    fmid = (fmin + fmax)/2.0
    band = band_classifier(fmid)

    fil_parameters = {'fmin':fmin, 'fmax':fmax, 'bandwidth':abs(bandwidth), 'band':band} 

    return fil_parameters

print params(filename)

#print fil_parameters(filename)['fmin'], fil_parameters(filename)['fmax']





#print fil_parameters(filename)

#fmin=fil_parameters(filename)['fmin']
#fmax=fil_parameters(filename)['fmax']

#if fmin <= 2400 <= fmax:
  #  with open('wifi.txt', 'a+') as file:
 #       file.write('%s' % (filename))
#else:
#    print 'does not contain wifi'
