def gauss(x, mu, sig):
	#This function returns the ordinate value for a Gaussian distribution evaluated at a given abscissa value for a given mean and stddev.
	import numpy as np
	return (np.exp(-(x-mu)**2))/(2*sig**2)


def gauss_power():
	import numpy as np
	import matplotlib.pyplot as plt

	N = 300  #Number of samplings
	T = 1./30. #Time (s) between each sampling

	t = np.arange(0, N*T, T) #N*T is total time elapsed, while T is step size since there are T seconds between each sampling. The values of t are the times at which samplings occur.

	data_gauss = np.random.normal(0, 1, len(t)) #Normally distributed noise over time.
	ps_gauss = np.abs(np.fft.fft(data_gauss))**2 #Power spectrum of Gaussian noise.  
	freqs_gauss = np.fft.fftfreq(len(data_gauss), T) #Gives frequencies present
	idx_gauss = np.argsort(freqs_gauss) #Gives indices of freqs sorted from low to high freq.

	data_superpos = data_gauss + np.sin(2*np.pi*5*t) #Gaussian superposed with sinusoidal time series.
	ps_superpos = np.abs(np.fft.fft(data_superpos))**2
	freqs_superpos = np.fft.fftfreq(len(data_gauss), T)
	idx_superpos = np.argsort(freqs_superpos)

	plt.figure(1)
	plt.subplot(221)
	plt.plot(t, data_gauss)
	plt.title("Gaussian Noise over Time")
	plt.xlabel("Time (s)")
	plt.ylabel("Amplitude")
	plt.grid()

	plt.subplot(222)
	plt.plot(freqs_gauss[idx_gauss], ps_gauss[idx_gauss]) #freqs_gauss[idx_gauss] orders the frequencies on the abscissa from most negative to most positive. ps_gauss[idx_gauss] gives values of power spectrum evaluated at each index.
	plt.title("Gaussian Power Spectrum")
	plt.xlabel("Frequency (Hz)")
	plt.ylabel("Power Spectral Density")
	plt.grid()

	plt.subplot(223)
	plt.plot(t, data_superpos)
	plt.title("Gaussian Noise + Sinusoid")
	plt.xlabel("Time (s)")
	plt.ylabel("Amplitude")
	plt.grid()

	plt.subplot(224)
	plt.plot(freqs_superpos[idx_superpos], ps_superpos[idx_superpos])
	plt.title("Gaussian + Sinusoid Power Spectrum")
	plt.xlabel("Frequency (Hz)")
	plt.ylabel("Power Spectral Density")
	plt.grid()

	plt.show()



