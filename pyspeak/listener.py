import audioop
import logging
import os
import pyaudio
import subprocess
import urllib
import urllib2
import wave
from collections import deque

class Listener():
    LANGUAGE = 'en-US'
    MAX_RESULTS = 6

    def __init__(self, destination_filename='pyaudio_file', silence_time=2, threshold=20, bits=pyaudio.paInt16, channels=1, rate=44100, chunk=1024):
        logging.info('PySpeak listener initializing')
        self.pyaudio_handler = pyaudio.PyAudio()
        device_input_index = self._find_input_device_index()
        if not self.pyaudio_handler.is_format_supported(input_device=device_input_index, rate=rate, input_channels=channels, input_format=bits):
            logging.error('Unsupported format given while initializing')
            exit(1)

        self._all_chunks = []
        self.destination_filename = destination_filename
        self.bits = bits
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.silence_time = silence_time
        self.threshold = threshold

    def start(self):
        logging.info('Listening for speech input')
        self.stream = self.pyaudio_handler.open(format=self.bits,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk)

        rel = self.rate/self.chunk
        sliding_window = deque(maxlen=self.silence_time*rel)
        started = False

        while (True):
            try:
                data = self.stream.read(self.chunk)
            except IOError as e:
                data = '\x00' * self.chunk
                logging.warning('Probably just a hiccup in the recording: ' + str(e))

            sliding_window.append(abs(audioop.avg(data, 2)))

            if(True in [ x>self.threshold for x in sliding_window]):
                if(not started):
                    logging.info('Speech input detected.  Recording raw audio')
                started = True
                self._all_chunks.append(data)
            elif(started == True):
                logging.info('Speech input no longer detected')
                self._write()
                self._get_google_transciption()
                started = False
                sliding_window = deque(maxlen=self.silence_time*rel)
                self._all_chunks = []

        logging.info('Completed listening for speech input')
        self.stop()

    def stop(self):
        logging.info('Stopping speech input detection')
        self.stream.close()
        self.pyaudio_handler.terminate()

    def _find_input_device_index(self):
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
            logging.warning('No preferred input found; using default input device.')

        return device_index


    def _write(self):
        logging.info('Writing out speech input')
        data = ''.join(self._all_chunks)
        wav_file = wave.open(self.destination_filename + '.wav', 'wb')
        wav_file.setnchannels(self.channels)
        wav_file.setsampwidth(self.pyaudio_handler.get_sample_size(self.bits))
        wav_file.setframerate(self.rate)
        wav_file.writeframes(data)
        wav_file.close()
        logging.info('Completed writing out files for the destination filename %s' % self.destination_filename)


    def _get_google_transciption(self):
        #Convert to flac
        logging.info('Opening speech input WAV file and converting to FLAC')
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(['flac', '-f', self.destination_filename + '.wav'], stdout=devnull, stderr=subprocess.STDOUT)
        file_handle = open(self.destination_filename + '.flac','rb')
        flac_cont = file_handle.read()
        file_handle.close()

        logging.info('Sending FLAC speech input to Google for interpretation')
        google_speech_url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=%s' % (self.LANGUAGE, self.MAX_RESULTS)
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",'Content-type': 'audio/x-flac; rate=%s' % (self.rate)}
        request = urllib2.Request(google_speech_url, data=flac_cont, headers=headers)
        url_handle = urllib2.urlopen(request)
        result = eval(url_handle.read())['hypotheses']
        logging.info('Got response from Google: ' + str(result))
        logging.info('Removing speech input WAV and FLAC files')
        map(os.remove, ([self.destination_filename + '.wav', self.destination_filename + '.flac']))
        return result

