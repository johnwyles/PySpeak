import urllib
import urllib2
from pprint import pprint


class Speaker():
    def __init__(self):
        # Do nothing
        return


    def __del__(self):
        # Do nothing
        return


    def get_google_translation(self, language='en', phrase=''):
        google_translation_api_url = 'http://translate.google.com/translate_tts'
        url_values = {'tl': language, 'q': phrase}
        url_data = urllib.urlencode(url_values)
        pprint(google_translation_api_url)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7'}
        request = urllib2.Request(google_translation_api_url, data=url_data, headers=headers)
        url_handle = urllib2.urlopen(request)
        file_handle = open("data.mp3", "wb")
        file_handle.write(url_handle.read())
        file_handle.close()
