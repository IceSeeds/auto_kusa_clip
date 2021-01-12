
import librosa
from librosa import display
import matplotlib.pyplot as plt
import pydub

import sys
import scipy.io.wavfile
import numpy as np


import speech_recognition as sr

def make_waveform_pyplot( filename ):


    #音声ファイル読み込み
    args = sys.argv
    #filename = args[1]
    rate, data = scipy.io.wavfile.read(filename)

    ##### 音声データをそのまま表示する #####
    #縦軸（振幅）の配列を作成   #16bitの音声ファイルのデータを-1から1に正規化
    data = data / 32768
    #横軸（時間）の配列を作成　　#np.arange(初項, 等差数列の終点, 等差)
    time = np.arange(0, data.shape[0]/rate, 1/rate)
    #データプロット
    plt.plot(time, data)
    plt.show()
    result = []
    test = {}

    for t, d in zip( time, data ):
        #if ( d >= 0.4 ) or ( d <= -0.4 ):
        print( d )
        test['time'] = t
        test['data'] = d
    #    result.append( test )
    #print( data )
    #print( result )


def mp3_to_wave( in_mp3, out_wav ):
        sound = pydub.AudioSegment.from_mp3( in_mp3 )
        sound.export( out_wav, format = "wav" )

def wav_to_text( wav_file ):
        r = sr.Recognizer()

        with sr.AudioFile( wav_file ) as source:
            audio = r.record( source )

        text = r.recognize_google( audio, language = 'ja-JP' )
        print( text.split(" ") )

        #with open( file_name, mode = "a", encoding="utf-8" ) as f:
        #    f.write( self.place +  " : " + str( self.text ) + "\n" )

#mp3_to_wave( "video/clip/ZBCPR7-9yZQ/mp3/2_clip_838.mp3", "test.wav" )
#wav_to_text( "test.wav" )

make_waveform_pyplot( "test.wav" )
