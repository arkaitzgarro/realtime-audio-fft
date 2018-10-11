import numpy
import pyaudio
import sys
import threading
import time

from src.fft import getFFT

class GDPR:
    """
    The GDPR class is provides access to continuously recorded
    (and mathematically processed) microphone data.

    Arguments:

        device - the number of the sound card input to use.

        rate - sample rate to use. Defaults to something supported.

        updatesPerSecond - how fast to record new data. Note that smaller
        numbers allow more data to be accessed and therefore high
        frequencies to be analyzed if using a FFT later
    """

    def __init__(self, device = None, rate = None, updatesPerSecond = 10):
        self.pa = pyaudio.PyAudio()
        self.chunk = 1024 # gets replaced automatically
        self.updatesPerSecond = updatesPerSecond
        self.chunksRead = 0
        self.device = device
        self.rate = rate

    ### SETUP AND SHUTDOWN

    def initiate(self):
        """Initialize our device and frequency rate"""
        if self.device is None:
            self.device = self.input_device()
        if self.rate is None:
            self.rate = self.valid_low_rate(self.device)
        # hold one tenth of a second in memory
        self.chunk = int(self.rate / self.updatesPerSecond)
        self.datax = numpy.arange(self.chunk) / float(self.rate)
        msg = 'Recording from "%s" ' % self.info["name"]
        msg += 'at %d Hz' % self.rate
        print(msg)

    def pause(self):
        """Gently pause the recording"""
        print("👋  Sending stream termination command...")
        # The threads should self-close
        self.keepRecording = False
        # Wait for all threads to close
        while(self.t.isAlive()):
            time.sleep(.1)
        self.stream.stop_stream()
        # self.pa.terminate()

    ### STREAM HANDLING

    def stream_start(self):
        """adds data to self.data until termination signal"""
        self.initiate()
        print("🎙  Starting stream...", self.chunk, self.rate)
        # set this to False later to terminate stream
        self.keepRecording = True
        # Will fill up with threaded recording data
        self.data = None
        self.fft = None
        self.dataFiltered = None
        # Open the microphone
        self.stream = self.pa.open(
            format = pyaudio.paInt16,
            channels = 1,
            rate = self.rate,
            input=True,
            frames_per_buffer = self.chunk
        )
        self.stream_thread_new()

    ### STREAM HANDLING

    def stream_thread_new(self):
        self.t = threading.Thread(target = self.stream_readchunk)
        self.t.start()

    def stream_readchunk(self):
        """Reads some audio and re-launches itself"""
        try:
            self.data = numpy.fromstring(self.stream.read(self.chunk), dtype = numpy.int16)
            self.fftx, self.fft = getFFT(self.data, self.rate)

        except Exception as E:
            print("💩  Something bad happen. Terminating...")
            print(E)
            self.keepRecording = False

        if self.keepRecording:
            self.stream_thread_new()
        else:
            self.stream.close()
            # self.pa.terminate()
            print("🛑  Stream STOPPED")
            self.chunksRead += 1

    ### DEVICE TESTING

    def valid_low_rate(self, device):
        """Set the rate to the lowest supported audio rate."""
        for testrate in [44100]:
            if self.test_device(device, testrate):
                return testrate
        print("SOMETHING'S WRONG! I can't figure out how to use DEVICE =>", device)
        return None

    def test_device(self, device, rate = 44100):
        """given a device ID and a rate, return True/False if it's valid."""
        try:
            self.info = self.pa.get_device_info_by_index(device)
            if not self.info["maxInputChannels"] > 0:
                return False
            stream = self.pa.open(
                format = pyaudio.paInt16,
                channels = 1,
                input_device_index=device,
                frames_per_buffer=self.chunk,
                rate = int(self.info["defaultSampleRate"]
            ), input = True)
            stream.close()
            return True
        except:
            return False

    def input_device(self):
        """
        See which devices can be opened for microphone input.
        Return the first valid device
        """
        mics=[]
        for device in range(self.pa.get_device_count()):
            if self.test_device(device, self.rate):
                mics.append(device)
        if len(mics) == 0:
            print("No microphone devices found!")
            sys.exit()
        print("Found %d microphone device(s)" % len(mics))
        return mics[0]
