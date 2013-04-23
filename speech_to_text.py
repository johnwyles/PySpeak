import argparse
import audioop
import logging
import os
import pyaudio
import wave
import time
import urllib
import urllib2
from pprint import pprint
from collections import deque


class Listener():
    LANGUAGE = 'en-US'
    MAX_RESULTS = 6

    def __init__(self, destination='file', silence_limit=2, threshold=20, bits=pyaudio.paInt16, channels=1, rate=16000, chunk=1024):
        self.destination = destination
        self.all_chunks = []
        self.bits = bits
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.silence_limit = silence_limit
        self.threshold = threshold
        self.recorded_chunks = 0

    def start(self):
        logging.info('Listening for speech input')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format = self.bits,
              channels = self.channels,
              rate = self.rate,
              input = True,
              frames_per_buffer = self.chunk)

        rel = self.rate/self.chunk
        sliding_window = deque(maxlen=self.silence_limit*rel)
        started = False

        while (True):
            try:
                data = self.stream.read(self.chunk)
            except IOError as e:
                data = '\x00' * self.chunk
                print e

            sliding_window.append(abs(audioop.avg(data, 2)))

            if(True in [ x>self.threshold for x in sliding_window]):
                if(not started):
                    logging.info('Speech input detected.  Recording raw audio')
                started = True
                self.all_chunks.append(data)
            elif(started == True):
                logging.info('Speech input no longer detected')
                data = ''.join(self.all_chunks)
                wf = wave.open(self.destination + '.wav', 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.bits))
                wf.setframerate(self.rate)
                wf.writeframes(data)
                wf.close()
                self.stt_google_wav()
                started = False
                sliding_window = deque(maxlen=self.silence_limit*rel)
                self.all_chunks = []

        print logging.info('Completed listening for speech input')
        self.stop()


    def stop(self):
        print logging.info('Stopping speech input detection')
        self.stream.close()
        self.p.terminate()

        print logging.info('Writing out speech input')
        # write data to WAVE file
        data = ''.join(self.all_chunks)
        wf = wave.open(self.destination, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.bits))
        wf.setframerate(self.rate)
        wf.writeframes(self.all_chunks)
        wf.close()
        print "* saved: %s" % self.destination


    def stt_google_wav(self):
        #Convert to flac
        logging.info('Opening speech input WAV file and converting to FLAC')
        os.system("flac -f " + self.destination + '.wav')
        file_handle = open(self.destination + '.flac','rb')
        flac_cont = file_handle.read()
        file_handle.close()

        logging.info('Sending FLAC speech input to Google for interpretation')
        google_speech_url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=%s'%(self.LANGUAGE, self.MAX_RESULTS)
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",'Content-type': 'audio/x-flac; rate=%s'%(self.rate)}
        request = urllib2.Request(google_speech_url, data=flac_cont, headers=headers)
        url_handle = urllib2.urlopen(request)
        result = eval(url_handle.read())['hypotheses']
        logging.info('Got response from Google: ' + result)
        logging.info('Removing speech input WAV and FLAC files')
        map(os.remove, ([self.destination + '.wav', self.destination + '.flac']))
        return result


if __name__ == '__main__':
    APP_NAME = 'pyspeak'
    APP_VERSION = '0.0.1'

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--loglevel', default='INFO', help='Log level for console output (DEBUG, INFO, WARNING, ERROR, CRITICAL')
    parser.add_argument('-v', '--version', help='Get the version number and exit', const='version', nargs='?')
    arguments = parser.parse_args()

    # Print the version number and exit
    if arguments.version:
        print APP_NAME + ": " + APP_VERSION
        exit()

    # Setup logging
    try:
        number_level = getattr(logging, arguments.loglevel.upper(), None)
        if not isinstance(number_level, int):
            raise ValueError('Invalid log level: %s' % number_level)
    except:
        number_level

    logging.basicConfig(format='[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s', level=number_level, nargs='?')

    # Setup the speech listener
    listener = Listener()
    listener.start()
