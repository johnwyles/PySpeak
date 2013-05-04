import audioop
import logging
import os
import pyaudio
import subprocess
import urllib
import urllib2
import wave
import collections
from pprint import pprint


class Listener():
    """
    Listener class

    TODO(): put more infoation here
    """
    def __init__(self, filename_prefix='pyspeak_file', silence_time=2, threshold=80, language='en-US', max_results=4, bits=pyaudio.paInt16, channels=1, rate=44100, chunk=2048):
        """
        Setup the pyaudio instance and other initialize other instance variables
        """
        logging.info('Listener is initializing')
        
        # Make sure the format is initialized
        self.pyaudio_handler = pyaudio.PyAudio()
        device_input_index = self._find_input_device_index()
        if not self.pyaudio_handler.is_format_supported(input_device=device_input_index, rate=rate, input_channels=channels, input_format=bits):
            logging.error('Unsupported format given while initializing')
            exit(1)

        # Instance variables
        self._all_chunks = []
        self.bits = bits
        self.channels = channels
        self.chunk = chunk
        self.filename_prefix = filename_prefix
        self.language = language
        self.max_results = max_results
        self.rate = rate
        self.silence_time = silence_time
        self.threshold = threshold


    def __del__(self):
        """
        Destructor to teardown the pyaudio instance we created
        """
        self.pyaudio_handler.terminate()


    def get_utterance(self):
        """
        TODO(): Put a ton of information here
        """
        # Do some initialization
        window_size = self.silence_time*(self.rate/self.chunk)
        sliding_window = collections.deque(maxlen=window_size)
        utterance = None

        # Setup the pyaudio stream
        logging.info('Listening for speech input')
        self.stream = self.pyaudio_handler.open(format=self.bits,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk)

        # Start recording some data
        started = False
        recording = True
        while (recording):
            # Get a chunk of data from the stream
            try:
                data = self.stream.read(self.chunk)
            except IOError as e:
                data = '\x00' * self.chunk
                logging.warning('Probably just a hiccup in the recording: ' + str(e))

            # Get average of the last two bytes in the window and keep track of it
            sliding_window.append(abs(audioop.avg(data, 2)))

            # If the average of the chunk exceeds the threshold keep the data
            if(True in [x>self.threshold for x in sliding_window]):
                if(not started):
                    logging.info('Speech input detected.  Recording raw audio')
                started = True
                self._all_chunks.append(data)

            # If the average of the chunk is
            elif(started):
                logging.info('Speech input no longer detected')
                recording = False
                self._write()
                utterance = self._get_google_transciption()
                sliding_window = collections.deque(maxlen=window_size)
                self._all_chunks = []
                self.stream.close()

        return utterance


    def _find_input_device_index(self):
        """
        Find the audio input device by looking through the known devices

        TODO(): Put information about the return
        """
        device_index = None            
        for i in range( self.pyaudio_handler.get_device_count() ):     
            devinfo = self.pyaudio_handler.get_device_info_by_index(i)   
            logging.debug("Device %d: %s" % (i, devinfo["name"]))

            for keyword in ["mic", "input"]:
                if keyword in devinfo["name"].lower():
                    logging.info("Found input: %d - %s" % (i, devinfo["name"]))
                    device_index = i
                    return device_index

        if device_index == None:
            logging.warning('No preferred input found; using default input device')

        return device_index


    def _write(self):
        """
        Helper method write out the recorded contents
        """
        logging.info('Writing out speech input')
        data = ''.join(self._all_chunks)
        wav_file = wave.open(self.filename_prefix + '.wav', 'wb')
        wav_file.setnchannels(self.channels)
        wav_file.setsampwidth(self.pyaudio_handler.get_sample_size(self.bits))
        wav_file.setframerate(self.rate)
        wav_file.writeframes(data)
        wav_file.close()

        logging.info('Opening speech input WAV file and converting to FLAC')
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(['flac', '-f', self.filename_prefix + '.wav'], stdout=devnull, stderr=subprocess.STDOUT)


    def _get_google_transciption(self):
        """
        Call the Google speech API to get the transcription for the FLAC encoded data

        TODO(): Put information about the return
        """
        logging.info('Getting FLAC file contents')
        file_handle = open(self.filename_prefix + '.flac','rb')
        flac_cont = file_handle.read()
        file_handle.close()

        logging.info('Sending FLAC speech input to Google for interpretation')
        google_speech_api_url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=%s'%(self.language, self.max_results)
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",'Content-type': 'audio/x-flac; rate=%s'%(self.rate)}
        request = urllib2.Request(google_speech_api_url, data=flac_cont, headers=headers)
        url_handle = urllib2.urlopen(request)

        result = eval(url_handle.read())['hypotheses']
        logging.info('Got response from Google: ' + str(result))

        logging.info('Removing speech input WAV and FLAC files')
        map(os.remove, ([self.filename_prefix+'.wav', self.filename_prefix+'.flac']))

        return result
