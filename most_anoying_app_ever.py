import numpy as np
import pygame
import time
import os
import threading

#google speech recognition stuff
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import io

#record stuff
import wave
import pyaudio
from array import array
from struct import pack

class code (object):

    def setup(self):
        #set up veriables
        self.profanity_filter = bool(int(input("profanity filter OFF[0] ON[1]")))
        self.played_minimum = 0
        self.sample_rate = 16000
        self.phrase = ["",""]
        self.largest = -1
        self.adress = os.getcwd() + "\\info\\"
        self.record_address = self.adress + "recording\\"
        self.Title = "most anoying app ever: 0"
        self.played_minimum = 0
        self.database_read_in(self.adress)
        #set up states
        pygame.init()
        os.system("title "+self.Title)
        self.audio_CHUNK_SIZE = 1024
        self.audio_FORMAT = pyaudio.paInt16
        self.audio_RATE = self.sample_rate
        self.stream = pyaudio.PyAudio().open(format=self.audio_FORMAT, channels=1, rate=self.audio_RATE,
                                             input=True, output=True,
                                             frames_per_buffer=self.audio_CHUNK_SIZE)
        self.record(2,self.record_address+"start.wav")
        os.system('cls')
        return

    def main(self):
        self.setup()
        lenght_of_rec = 2
        self.loop = 0

        thread_record     = threading.Thread(target = self.long_time_record        , name=0 , args=(lenght_of_rec,))

        thread_record.start()

        while True:
            self.phrase = ["",""]
            if self.loop <= self.largest:
                
                phrase = self.transcribe_file(0,self.record_address+str(self.loop)+".wav")
                phrase = phrase.lower()
                self.loop+=1
                self.phrase_to_music(phrase)
            
        return

    def long_time_record(self,lenght_of_rec):
        print("start thread:" + "record")
        loop = 0
        while True:
            self.record(lenght_of_rec,self.record_address+str(loop)+".wav")
            self.largest = loop
            loop+=1
        print("thread exit:" + "record")
        return

    def record(self,lenght_of_rec,file_name):
        lenght_of_rec = lenght_of_rec * (self.audio_RATE / self.audio_CHUNK_SIZE)

     
        r = array('h')
        loop = 0
        while 1:
            # little endian, signed short
            snd_data = array('h', self.stream.read(self.audio_CHUNK_SIZE))
            r.extend(snd_data)

            loop += 1
            if loop > lenght_of_rec:
                break


        sample_width = pyaudio.PyAudio().get_sample_size(self.audio_FORMAT)
        data = pack('<' + ('h'*len(r)), *r)

        wf = wave.open(file_name, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(self.audio_RATE)
        wf.writeframes(data)
        wf.close()
        return

    def transcribe_file(self,thread,file_name):
        client = speech.SpeechClient()
        content = io.open(file_name, 'rb').read()
        stream = [content]
        requests = (types.StreamingRecognizeRequest(audio_content=chunk)for chunk in stream)

        config = types.RecognitionConfig(
        encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=self.sample_rate,
        language_code='en-GB',
        max_alternatives = 1,
        profanity_filter=self.profanity_filter,
        #speech_contexts = self.speech_context,
        )

        streaming_config = types.StreamingRecognitionConfig(config=config)

        responses = client.streaming_recognize(streaming_config, requests)
        for response in responses:
            for result in response.results:
                alternatives = result.alternatives
                for alternative in alternatives:
                    self.phrase[thread] = alternative.transcript
                    return alternative.transcript

        return ""

    def phrase_to_music(self,phrase):
        if phrase == "stop":
            pygame.mixer.music.stop()
            self.played_minimum = 0
        elif self.profanity_filter and "*" in phrase:# if profanity_filter = True
            sound = pygame.mixer.music
            sound.load(self.adress + "warning" + ".ogg")
            sound.play()
        elif self.played_minimum <= time.time():
            match_found , song_info = self.phrase_match(phrase)
            if match_found == True:
               print(song_info)
               self.played_minimum = self.play_song(song_info)
            else:
                print("no match!")
        else:
            print("still playing")

        self.output(phrase)
        return
    
    def output(self,phrase):
        #os.system('cls')
        self.Title = "most anoying app ever: " + str(self.loop) + " / " + str(self.largest)
        os.system("title "+self.Title)

        print(self.database)
        print("lenght: " + str(self.lenght_of_database))
        print(phrase)
        return

    def database_read_in (self,adress):
        adress = adress + "databases\\"
        adress = adress + "basic.txt"
        file = open(adress,"r")
        file.readline()
    
        read = file.readline()
        read = read[:len(read)-1]
        read = read.split(",")
        database = [read]
        self.lenght_of_database = 1
        while True:
            read = file.readline()
            if read == "__end of file__":
                break
            else:
                read = read[:len(read)-1]
                read = [read.split(",")]
                database = database + read
                self.lenght_of_database += 1
            
        file.close()
        self.database = np.asarray(database)
        return self.database , self.lenght_of_database
    
    def phrase_match(self,phrase):
        match_found = False
        best_match = None
        phrase = phrase.split(" ")
        for loop in range(len(phrase)):
            for loop2 in range(self.lenght_of_database):
                if self.database[loop2][0] == phrase[loop]:
                    match_found = True
                    best_match = self.database[loop2]
                    break
    
        return match_found , best_match
    
    def play_song (self,song_info):
        adress = self.adress + "music\\"
        sound = pygame.mixer.music
        file_name = str(song_info[1])
        start_time = float(song_info[2])
        minimum_time = float(song_info[3])
    
        adress = adress + file_name + ".ogg"
        sound.load(adress)
        sound.play(start = start_time)
        played_minimum = time.time() + minimum_time
    
        return played_minimum

code = code()
code.main()