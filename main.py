import numpy
import time

import src.gdpr as GDPR

# maxFFT = 0
PCM_THRESHOLD = 5000

ear = GDPR.GDPR(updatesPerSecond = 5)
ear.stream_start()

while True:
    if not ear.data is None and not ear.fft is None:
        pcm = numpy.max(numpy.abs(ear.data))
        fft = numpy.max(numpy.abs(ear.fft))
        print(fft)
        # if pcm > PCM_THRESHOLD:
        #     maxPCM = pcm
        #     ear.pause()
        #     print("PCM %d" % pcm)
        #     time.sleep(1)
        #     ear.stream_start()
        # if numpy.max(ear.fft) > maxFFT:
        #     maxFFT = numpy.max(numpy.abs(ear.fft))
