import argparse
import audioop
import logging
import os
import pyaudio
import subprocess
import time
import urllib
import urllib2
import wave
from pprint import pprint
from collections import deque

APP_NAME = 'pyspeak'
APP_VERSION = '0.0.1'

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


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    # parser.add_argument('-t', '--threshold', action=ValidateListenerArguments, help='The threshold for microphone sensitivity ()')
    # parser.add_argument('-f', '--destination-filename', action=ValidateListenerArguments, help='The temporary filename and location for the recorded before it goes off to Google')
    parser.add_argument('-l', '--loglevel', default='INFO', help='Log level for console output (DEBUG, INFO, WARNING, ERROR, CRITICAL')
    parser.add_argument('-v', '--version', help='Get the version number and exit', const='version', nargs='?')
    arguments = parser.parse_args()

    # Print the version number and exit
    if arguments.version:
        print APP_NAME + ": " + APP_VERSION
        exit(0)

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

# class ValidateListenerArguments(argparse.Action):
#     def __call__(self, parser, args, values, option_string=None):
#         # print '{n} {v} {o}'.format(n=args, v=values, o=option_string)
#         valid_subjects = ('foo', 'bar')
#         subject, credits = values
#         if subject not in valid_subjects:
#             raise ValueError('invalid subject {s!r}'.format(s=subject))
#         credits = float(credits)
#         Credits = collections.namedtuple('Credits', 'subject required')
#         setattr(args, self.dest, Credits(subject, credits))