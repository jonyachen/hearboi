"""
PyAudio exmple: Record a few seconds of audio and save to a WAVE
file.
"""
import pyaudio
import wave
import sys

from dejavu import Dejavu

CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1L
RATE = 48000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "/sounds/output.wav"

if sys.platform == 'darwin':
    CHANNELS = 1

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=1,
                frames_per_buffer=CHUNK,
                rate=RATE,
                input=True,
                input_device_index= 4)

print("* recording")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

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
