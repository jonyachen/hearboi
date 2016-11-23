mport pyaudio
import wave
import urllib2
import thread
import time
import requests

CHUNK = 1024 
FORMAT = pyaudio.paInt16 #paInt8
CHANNELS = 2 
RATE = 44100 #sample rate
filename = "output.wav"
website = 'http://ec2-54-71-180-108.us-west-2.compute.amazonaws.com/hearboi/device/record/status'
status = 'STOP'

def recordAudio(threadname):
    global status
    print (threadname)
    while True:
        p = pyaudio.PyAudio()
    
        while status=='STOP':
            time.sleep(0.5)
        
        print("* start recording")
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK) #buffer
        frames = []

        #for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        while(status=='START'):
            data = stream.read(CHUNK)
            frames.append(data) # 2 bytes(16 bits) per channel

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

