import numpy

def getFFT(data, rate):
    """Given some data and rate, returns FFTfreq and FFT (half)."""
    data = data * numpy.hamming(len(data))
    fft = numpy.fft.fft(data)
    fft = numpy.abs(fft)
    # fft = 10 * numpy.log10(fft)
    freq = numpy.fft.fftfreq(len(fft), 1.0 / rate)
    return freq[:int(len(freq) / 2)], fft[:int(len(fft) / 2)]
