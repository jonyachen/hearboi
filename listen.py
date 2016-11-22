import pyaudio
import wave
import audioop
import warnings
import json
warnings.filterwarnings("ignore")

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer, MicrophoneRecognizer

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "recording.wav"
THRESHOLD = 2000

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
print "listening..."
frames = []

while True:
    data = stream.read(CHUNK)
    level = audioop.rms(data, 2)
    #print "%s" % level
    if level > THRESHOLD:
        #print "%s" % level
	print "broken threshold"
	break

print "recording"
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print "finished recording"


# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()


config = {
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "M914ktIkP!",
        "db": "sound_db",
    }
}

# create a Dejavu instance
djv = Dejavu(config)

# Fingerprint all the mp3's in the directory we give it
djv.fingerprint_directory("sounds", [".wav"])

# Prints total number of fingerprints - for debugging
#print djv.db.get_num_fingerprints()

# Recognize audio from a file
song = djv.recognize(FileRecognizer, "recording.wav")
print "From file we recognized: %s\n" % song
