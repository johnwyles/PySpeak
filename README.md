PySpeak
=======
By: John Wyles
Email: john@johnwyles.com
Git: https://github.com/johnwyles/pyspeak

Python Speech Recognition, Voice Recognition, Text-to-Speech and Voice Command Engine

Requirements:
  - portaudio (http://portaudio.com/docs/v19-doxydocs/tutorial_start.html)
  - pyaudio (http://people.csail.mit.edu/hubert/pyaudio/compilation.html)

Setup:
  - MacOS X
	  - Install Homebrew if you don't already have it

		    ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"

	  - Install portaudio and flac from Homebrew

		    brew install portaudio flac

		    brew link portaudio flac

  - Linux
	  - Ensure you have portaudio

		    sudo yum -y install portaudio-devel flac-devel # for Fedora/RedHat distros

		    sudo apt-get install libportaudio-dev libflac-dev # for Ubuntu/Debian distros

  - Windows
	  - Good luck! :)

Installation:
    sudo pip install pyspeak

Usage:  
    usage: pyspeak [-h] [-l LOGLEVEL] [-v [VERSION]]

    optional arguments:
      -h, --help            show this help message and exit
      -l LOGLEVEL, --loglevel LOGLEVEL
                            Log level for console output (DEBUG, INFO, WARNING,
                            ERROR, CRITICAL
      -v [VERSION], --version [VERSION]
                            Get the version number and exit
