import pyaudio
import wave
import audioop
from collections import deque 
import os
import urllib2
import urllib
import time

from pprint import pprint

class Listener():
    def __init__(self, destination='file', silence_limit=2, threshold=20, bits=pyaudio.paInt16, channels=1, rate=16000, chunk=1024):
        #where to store the file on stop
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
        print "* listening. CTRL+C to finish."
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format = self.bits,
              channels = self.channels,
              rate = self.rate,
              input = True,
              frames_per_buffer = self.chunk)
        print "* recording"
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
                    print "...starting record"
                started = True
                self.all_chunks.append(data)
            elif(started == True):
                print "...finished"
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
                print "...listening"

        print "* done recording"
        self.stop()


    def stop(self):
        print "* done recording"
        self.stream.close()
        self.p.terminate()

        print "* saving"
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
        os.system("flac -f " + self.destination + '.wav')
        f = open(self.destination + '.flac','rb')
        flac_cont = f.read()
        f.close()

        #post it
        lang_code='en-US'
        googl_speech_url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=6'%(lang_code)
        hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",'Content-type': 'audio/x-flac; rate=44100'}
        req = urllib2.Request(googl_speech_url, data=flac_cont, headers=hrs)
        p = urllib2.urlopen(req)

        res = eval(p.read())['hypotheses']
        print res
        map(os.remove, ([self.destination + '.wav', self.destination + '.flac']))
        return res


l = Listener()
l.start()
