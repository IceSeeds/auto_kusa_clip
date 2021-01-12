# coding: utf-8
import os
import time

import glob
import shutil
from pydub import AudioSegment
import moviepy.editor as mp
import cv2

class Join:

    def __init__( self, target_url ):
            self.target_url = target_url
            self.dir        = "video/clip/" + self.target_url

    def movie( self, sec ):
            if not os.path.exists( self.dir + "/end_out_" + self.target_url + ".mp4" ):
                # ディレクトリ内の動画をリストで取り出す
                files   = []
                num     = [ 0, 1, 2, 3, 4 ]

                for s, i in zip( sec, num ):
                    files.append( self.dir + "/next/"  + str( i ) + "_nextout_" + self.target_url + ".mp4" )
                    files.append( self.dir + "/movie/" + str( i ) + "_clip_text_" + str( s ) +".mp4" )

                files.append( self.dir + "/next/graph_nextout_" + self.target_url + ".mp4" )

                # 出力ファイル名
                out_path = "movie_out_" + self.target_url + ".mp4"
                # 形式はmp4
                fourcc = cv2.VideoWriter_fourcc('m','p','4','v')

                # 動画情報の取得
                movie = cv2.VideoCapture( files[1] )
                fps     = movie.get( cv2.CAP_PROP_FPS )
                height  = movie.get( cv2.CAP_PROP_FRAME_HEIGHT )
                width   = movie.get( cv2.CAP_PROP_FRAME_WIDTH )

                # 出力先のファイルを開く
                out = cv2.VideoWriter( out_path, int(fourcc), fps, ( int(width), int(height) ) )

                for movies in ( files ):
                    # 動画ファイルの読み込み，引数はビデオファイルのパス
                    movie = cv2.VideoCapture( movies )

                    if movie.isOpened() == True: # 正常に動画ファイルを読み込めたか確認
                        ret, frame = movie.read() # read():1コマ分のキャプチャ画像データを読み込む
                    else:
                        ret = False

                    while ret:
                        # 読み込んだフレームを書き込み
                        out.write( frame )
                        # 次のフレーム読み込み
                        ret, frame = movie.read()

                mp3_path = Join.__mp3( self, sec )
            else:
                print( "already end_clip final" )

    def __mp3( self, sec ):
            #連結させるため、最初だけ定義する方法もある。
            sound1_1    = AudioSegment.from_file( "video/bgm/3s.mp3", "mp3" )
            sound1      = AudioSegment.from_file( "video\clip/" + self.target_url + "/mp3/0_clip_" + str(sec[0]) + ".mp3",  "mp3" )
            sound2_1    = AudioSegment.from_file( "video/bgm/3s.mp3", "mp3" )
            sound2      = AudioSegment.from_file( "video\clip/" + self.target_url + "/mp3/1_clip_" + str(sec[1]) + ".mp3",  "mp3" )
            sound3_1    = AudioSegment.from_file( "video/bgm/3s.mp3", "mp3" )
            sound3      = AudioSegment.from_file( "video\clip/" + self.target_url + "/mp3/2_clip_" + str(sec[2]) + ".mp3",  "mp3" )
            sound4_1    = AudioSegment.from_file( "video/bgm/3s.mp3", "mp3" )
            sound4      = AudioSegment.from_file( "video\clip/" + self.target_url + "/mp3/3_clip_" + str(sec[3]) + ".mp3",  "mp3" )
            sound5_1    = AudioSegment.from_file( "video/bgm/3s.mp3", "mp3" )
            sound5      = AudioSegment.from_file( "video\clip/" + self.target_url + "/mp3/4_clip_" + str(sec[4]) + ".mp3",  "mp3" )
            sound6      = AudioSegment.from_file( "video/bgm/end.mp3", "mp3" )

            sound = sound1_1 + sound1 + sound2_1 + sound2 + sound3_1 + sound3 + sound4_1 + sound4 + sound5_1 + sound5 + sound6
            # 保存
            sound.export( "mp3_out_" + self.target_url + ".mp3", format = "mp3" )

            result = "mp3_out_" + self.target_url + ".mp3"

            return result


    def end_clip( self, movie_name, mp3_name, join_name ):
            print( "movie : " + movie_name + "\nmp3 : " + mp3_name )

            if not os.path.exists( self.dir + "/end_out_" + self.target_url + ".mp4" ):
                clip = mp.VideoFileClip( movie_name ).subclip()
                clip.write_videofile( self.dir + "/" + join_name, audio = mp3_name )

                shutil.rmtree( self.dir + "/next" )
                os.remove( movie_name )
                os.remove( mp3_name )

            else:
                print( "already end_clip final" )
