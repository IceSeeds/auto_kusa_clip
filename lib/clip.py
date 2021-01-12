# coding: utf-8
import os
import shutil

import moviepy.editor as mp

class Clip:

    def __init__( self, target_url ):
            self.target_url = target_url
            self.dir        = "video/clip/" + self.target_url

    def movie( self, start_sec, stop_sec, sec, num ):
            dir = self.dir + "/movie"

            if not os.path.exists( dir ):#ディレクトリがなかったら
                os.makedirs( dir )

            full_movie_path = 'video/full/clip_' + self.target_url + '.mp4'
            mp4_name      = num + "_clip_" + sec + ".mp4"

            if not os.path.exists( dir + "/" + mp4_name ):
                video = mp.VideoFileClip( full_movie_path )
                final = mp.CompositeVideoClip( [video] )
                final.subclip( start_sec, stop_sec ).write_videofile(
                    mp4_name,
                    codec           = 'libx264',
                    audio_codec     = 'aac',
                    temp_audiofile  = 'temp-audio.m4a',
                    remove_temp     = True
                )

                shutil.move( mp4_name, dir )
            else:
                print( 'already clip_movie' )

            #clipした動画から音声を取得するようにする。
            Clip.__mp3( self, sec, mp4_name, num )

            return 'clip complete'

    #テスト用
    #clip_function( "video/full/clip_FqrGLlQpCsg.mp4", 10, 20, "FqrGLlQpCsg", "500" )

    def __mp3( self, sec, mp4_name, num ):
            dir = self.dir + "/mp3"

            if not os.path.exists( dir ):#ディレクトリがなかったら
                os.makedirs( dir )

            mp3_name = num + "_clip_" + str( sec ) + ".mp3"

            path = self.dir + "/movie/" + mp4_name
            # Extract audio from input video.
            if not os.path.exists( dir + "/" + mp3_name ):
                clip_input = mp.VideoFileClip( path ).subclip()# 0s ~ 117s ( 1m57s )'0, 117'
                clip_input.audio.write_audiofile( mp3_name )

                shutil.move( mp3_name, dir )
            else:
                print( 'already clip_mp3' )


    #テスト用
    #clip_mp3( "video/full/clip_FqrGLlQpCsg.mp4", 10, 20, "FqrGLlQpCsg", "500" )
