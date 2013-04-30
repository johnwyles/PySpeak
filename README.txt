PySpeak
=======

By: John Wyles Email: john@johnwyles.com Git:
https://github.com/johnwyles/pyspeak

Python Speech Recognition, Voice Recognition, Text-to-Speech and Voice
Command Engine

Requirements: - portaudio
(http://portaudio.com/docs/v19-doxydocs/tutorial\_start.html) - pyaudio
(http://people.csail.mit.edu/hubert/pyaudio/compilation.html)

Setup: - MacOS X - Install Homebrew if you don't already have it

::

            ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"

      - Install portaudio and flac from Homebrew

            brew install portaudio flac

            brew link portaudio flac

-  Linux

   -  Ensure you have portaudio

      ::

          sudo yum -y install portaudio-devel flac-devel # for Fedora/RedHat distros

          sudo apt-get install libportaudio-dev libflac-dev # for Ubuntu/Debian distros

-  Windows

   -  Good luck! :)

Installation:

::

    sudo pip install pyspeak

Usage:

::

    usage: pyspeak [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-v]
                   {listen,speak} ...

    positional arguments:
      {listen,speak}        Subcommand for pyspeak to either listen for microphone
                            input (speech-to-text) or text input (text-to-speech)
        listen              Listen for microphone input (speech-to-text)
        speak               Listen for text input (text-to-speech

    optional arguments:
      -h, --help            show this help message and exit
      -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Log level for console output (default: INFO)
      -v, --version         Get the version number and exit (default: False)

