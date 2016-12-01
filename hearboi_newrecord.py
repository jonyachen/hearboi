import pyaudio
import wave
import sys
import urllib2
import thread
import time
import requests

CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
RECORD_SECONDS = 5
filename = "sounds/output.wav"
website = 'http://ec2-54-71-180-108.us-west-2.compute.amazonaws.com/hearboi/device/record/status'
status = 'STOP'

if sys.platform == 'darwin':
    CHANNELS = 1

def recordAudio(threadname):
    global status
    print (threadname)
    while True:
        p = pyaudio.PyAudio()
    
        while status=='STOP':
            time.sleep(1.5)
        
        print("* start recording")
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

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    
        # POST file to server
        urllib2.urlopen("http://ec2-54-71-180-108.us-west-2.compute.amazonaws.com/hearboi/device/record/stop")
        files = {'audioFile': open(filename, 'rb')}
        uploadSite = 'http://ec2-54-71-180-108.us-west-2.compute.amazonaws.com/hearboi/device/record/upload'
        r = requests.post(uploadSite, files=files)

def monitor(threadname):
    global status
    print (threadname)
    while True:
        try:
            status = urllib2.urlopen(website).read()
        except urllib2.HTTPError:
            time.sleep(1)
        time.sleep(0.5)

thread.start_new_thread(monitor,("monitor thread",))
thread.start_new_thread(recordAudio,("record thread",))

c = raw_input("Type something to quit.")

