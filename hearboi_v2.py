import pyaudio
import wave
import audioop
import warnings
import json
warnings.filterwarnings("ignore")
import urllib2
import thread
import time
import requests
import sys

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer, MicrophoneRecognizer
filename = "sounds/output.wav"
website = 'http://ec2-54-71-180-108.us-west-2.compute.amazonaws.com/hearboi/device/record/status'
status = 'STOP'

def monitor(threadname):
    global status
    print (threadname)
    while True:
        try:
            status = urllib2.urlopen(website).read()
        except urllib2.HTTPError:
            time.sleep(1)
        time.sleep(0.5)

def add_new_sound(audio, frames, info, name):
    FORMAT = info['FORMAT']
    CHANNELS = info['INFO']
    RATE = info['RATE']
    CHUNK = info['CHUNK']
    RECORD_SECONDS = info['RECORD_SECONDS']
    WAVE_OUTPUT_FILENAME = info['WAVE_OUTPUT_FILENAME']
    THRESHOLD = info['THRESHOLD']

    print "adding sound '%s' to soundsdb" % name
    waveFile = wave.open(name, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

def main(threadname):
    global status
    print (threadname)

    info = {
    'FORMAT' : pyaudio.paInt16,
    'CHANNELS' : 1,
    'RATE' : 48000,
    'CHUNK' : 8192,
    'RECORD_SECONDS' : 5,
    'WAVE_OUTPUT_FILENAME' : "recording.wav",
    'THRESHOLD' : 1000
    }

    audio = pyaudio.PyAudio()
    confidence_threshold = 5


    config = {
        "database": {
            "host": "127.0.0.1",
            "user": "root",
            "passwd": "rasp",
            "db": "sound_db",
        }
    }

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK,
            input_device_index=4)
    print "listening..."

    frames = []
    FORMAT = info['FORMAT']
    CHANNELS = info['INFO']
    RATE = info['RATE']
    CHUNK = info['CHUNK']
    RECORD_SECONDS = info['RECORD_SECONDS']
    WAVE_OUTPUT_FILENAME = info['WAVE_OUTPUT_FILENAME']
    THRESHOLD = info['THRESHOLD']

    # create a Dejavu instance
    djv = Dejavu(config)

    # Fingerprint all the mp3's in the directory we give it
    djv.fingerprint_directory("sounds", [".wav"])

    # Prints total number of fingerprints - for debugging
    print djv.db.get_num_fingerprints()

    record = False
    while True:

        # while status=='STOP':
        #     time.sleep(1.5)

        data = stream.read(CHUNK)
        level = audioop.rms(data, 2)
        #print "%s" % level
        if level > THRESHOLD or record:

            print "recording"
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            if status=='START':
                # name = get from server
                add_new_sound(audio, frames, info, filename)

                urllib2.urlopen("http://ec2-54-71-180-108.us-west-2.compute.amazonaws.com/hearboi/device/record/stop")
                files = {'audioFile': open(filename, 'rb')}
                uploadSite = 'http://ec2-54-71-180-108.us-west-2.compute.amazonaws.com/hearboi/device/record/upload'
                r = requests.post(uploadSite, files=files)

            else:
                add_new_sound(frames, info, info['WAVE_OUTPUT_FILENAME'])
                print "finished recording"

                song = djv.recognize(FileRecognizer, "recording.wav")
                song_name = song['song_name']
                if song['confidence'] > confidence_threshold:
                    print "From file we recognized: %s\n" % song

                    print "Alerting with SMS"
                    website = 'http://ec2-54-71-180-108.us-west-2.compute.amazonaws.com/hearboi/device/sendSMS/4'
                    urllib2.urlopen(website).read()


if __name__=='__main__':
    thread.start_new_thread(monitor,("monitor thread",))
    thread.start_new_thread(main,("main",))

    c = raw_input("Type something to quit.")

