# -*- coding: utf-8 -*-
import os
import shutil

import glob
from moviepy.editor import *
from PIL import Image

class ImageToVideo:

    def __init__( self, target_url ):
            self.target_url = target_url
            self.dir        = "video/clip/" + self.target_url

    #ランキング画像を動画にする。
    def movie( self, num ):
            if not os.path.exists( self.dir + '/next/' + str( num ) + "_nextout_" + self.target_url + ".mp4" ):
                img_name = str( num + 1 ) + "_image_" + self.target_url + ".png"
                #画像の複製
                if ImageToVideo.__copy( self, self.dir + "/image/" + img_name ):
                    # inputディレクトリ以下の拡張子が.jpgのファイル名リストを一括取得
                    file_list = glob.glob( r'video/clip/' + self.target_url + '/next/img/*.png' )#self.dirに変更
                    # ファイル名リストを昇順にソート
                    file_list.sort()

                    # スライドショーを作る元となる静止画情報を格納する処理
                    clips = []
                    for m in file_list:
                        clip = ImageClip( m ).set_duration( '00:00:00.02' )
                        clip = clip.resize( newsize = ( 1280, 720 ) )
                        clips.append( clip )

                    # スライドショーの動画像を作成する処理
                    concat_clip = concatenate_videoclips( clips, method = "compose" )
                    concat_clip.write_videofile( r'video/clip/' + self.target_url + '/next/' + str( num ) + "_nextout_" + self.target_url + ".mp4", fps = 30, write_logfile = False, )
                else:
                    print( "img_to_movie: False" )
            else:
                print( "already image_to_video movie" )

    #グラフの画像を元に動画を生成。
    def graph( self ):
            if not os.path.exists( self.dir + "/next/graph_nextout_" + self.target_url + ".mp4" ):
                if ImageToVideo.__copy( self, self.dir + "/img_" + self.target_url + ".png" ):
                    # inputディレクトリ以下の拡張子が.jpgのファイル名リストを一括取得
                    file_list = glob.glob( r'video/clip/' + self.target_url + '/next/img/*.png' )
                    # ファイル名リストを昇順にソート
                    file_list.sort()

                    # スライドショーを作る元となる静止画情報を格納する処理
                    clips = []
                    for m in file_list:
                        clip = ImageClip( m ).set_duration( '00:00:00.08' )
                        clip = clip.resize( newsize = ( 1280, 720 ) )
                        clips.append( clip )

                    # スライドショーの動画像を作成する処理
                    concat_clip = concatenate_videoclips( clips, method = "compose" )
                    concat_clip.write_videofile( r'video/clip/' + self.target_url + "/next/graph_nextout_" + self.target_url + ".mp4", fps = 30, write_logfile = False, )
                else:
                    print( "img_to_movie: False" )
            else:
                print( "already image_to_video graph" )

    #グラフの画像を複製
    def __copy( self, img_dir ):
            img_path = self.dir + '/next'

            if not os.path.isdir( img_path ):
                os.mkdir( img_path )

            #最終ファイルがなければ、作成
            if not os.path.exists( self.dir + "/end_out_" + self.target_url + ".mp4" ):
                if not os.path.isdir( img_path + "/img" ):
                    os.mkdir( img_path + "/img" )
                else:
                    shutil.rmtree( img_path + "/img" )
                    os.mkdir( img_path + "/img" )

                # 元画像の読み込み
                #originalImg = Image.open( "video/clip/" + self.target_url + "/image/" + self.img_name )
                originalImg = Image.open( img_dir )
                # 元画像のサイズを取得
                width, height = originalImg.size

                # 複製用のImageオブジェクト
                copyImg = Image.new( 'RGB', ( width, height ) )

                # 1px毎色を取得、詰め込み
                for y in range( height ):
                    for x in range( width ):
                        color = originalImg.getpixel( ( x, y ) )
                        copyImg.putpixel( ( x, y ), ( color[0], color[1], color[2] ) )

                for i in range( 0, 150 ):
                    # コピー画像の保存
                    copyImg.save( img_path + "/img/i_%d.png" % i )

                return True
            else:
                print( "already nextout movie" )
                return False


#self = ImageToVideo( 'y3XMjvXZYWM' )
#self.img_to_movie( "1_image_y3XMjvXZYWM.png", str( 0 ) )
#self.img_to_graph()
