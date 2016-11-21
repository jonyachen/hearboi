import warnings
import json
warnings.filterwarnings("ignore")

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer, MicrophoneRecognizer

config = {
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "M914ktIkP!", 
        "db": "sound_db",
    }
}

if __name__ == '__main__':

	# create a Dejavu instance
	djv = Dejavu(config)

	# Fingerprint all the mp3's in the directory we give it
	djv.fingerprint_directory("sounds", [".wav"])

	# Prints total number of fingerprints - for debugging
	#print djv.db.get_num_fingerprints()

	# Recognize audio from a file
	#song = djv.recognize(FileRecognizer, "sounds/fire_alarm.wav")
	#print "From file we recognized: %s\n" % song

	# Or recognize audio from your microphone for `secs` seconds
	secs = 5
	song = djv.recognize(MicrophoneRecognizer, seconds=secs)
	if song is None:
		print "Nothing recognized -- did you play the song out loud so your mic could hear it? :)"
	else:
		print "From mic with %d seconds we recognized: %s\n" % (secs, song)
