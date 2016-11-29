import pyaudio
import wave
import audioop
import warnings
import json
warnings.filterwarnings("ignore")
import urllib2

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer, MicrophoneRecognizer

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 8192
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "recording.wav"
THRESHOLD = 1000

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK,
		input_device_index=4)
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
        "passwd": "rasp",
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

if song:
    print "Alerting with SMS"
    website = 'http://ec2-54-71-180-108.us-west-2.compute.amazonaws.com/hearboi/device/sendSMS/4'
    urllib2.urlopen(website).read()
