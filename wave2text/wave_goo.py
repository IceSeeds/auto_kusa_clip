# coding: utf-8

import speech_recognition as sr
from pydub import AudioSegment
import wave
import numpy as np
import matplotlib.pyplot as plt

import librosa
import librosa.display

def out_text( wav_file ):
    r = sr.Recognizer()

    with sr.AudioFile( wav_file ) as source:
        audio = r.record( source )

    text = r.recognize_google( audio, language = 'ja-JP' )
    print( text )

def mp3_to_wav( mp3_path ):
    wav_path = "wave2text/t_285.wav"

    mp3 = AudioSegment.from_mp3( mp3_path )
    mp3.export( wav_path, format="wav" )

    return wav_path

def get_dB( wav_file ):
    SAMPLING_RATE = 44100
    Threshold = 0.75
    y, sr = librosa.load( wav_file, sr = SAMPLING_RATE )
    print( len( y ) )
    cnt = 0
    for i in y:
        if i >= Threshold:
            print( str( i ) + " : " + str( cnt / SAMPLING_RATE ) )
        cnt += 1

def main():
    wav = mp3_to_wav( "wave2text/0_clip_285.mp3" )
    out_text( "wave2text/t_285.wav" )


if __name__ == '__main__':
    main()

    #tempo, beat_frames = librosa.beat.beat_track( y = y, sr = sr )
    #beat_times = librosa.frames_to_time( beat_frames, sr = sr )
    #print( beat_times )
    #print( len( beat_times ) )

    #mpl_collection = librosa.display.waveplot( y, sr = sr )
    #mpl_collection.axes.set( title = "音声波形", ylabel = "波形の振幅" )
    #import matplotlib.pyplot as plt
    #plt.show()

#https://tips-memo.com/python-db
#https://self-development.info/python%E3%81%A7%E9%9F%B3%E5%A3%B0%E3%81%8B%E3%82%89%E3%83%86%E3%82%AD%E3%82%B9%E3%83%88%E3%81%B8%E5%A4%89%E6%8F%9B%E3%80%90speechrecognition%E3%80%91/
