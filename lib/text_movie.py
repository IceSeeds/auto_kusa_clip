# coding: utf-8
import os
import shutil

import numpy as np
import cv2
from PIL import ImageFont, ImageDraw, Image
import pickle

class Subtitles:

    def __init__( self, target_url ):
        self.target_url  = target_url
        self.dir         = 'video/clip/' + self.target_url

    #縁取り文字にする。
    def __set_font( draw, x, y, text, font, color, bold ):
        draw.text( ( x - bold, y - bold ), text, font = font, fill = color ) #文字列の挿入
        draw.text( ( x + bold, y - bold ), text, font = font, fill = color ) #文字列の挿入
        draw.text( ( x + bold, y + bold ), text, font = font, fill = color ) #文字列の挿入

    def __cv2_text( self, sec, start_msec, num ):
        mp4_file = self.dir + '/movie/' + num + '_clip_' + sec + '.mp4'

        cap     = cv2.VideoCapture( mp4_file )
        fps     = cap.get( cv2.CAP_PROP_FPS )
        width   = int( cap.get( cv2.CAP_PROP_FRAME_WIDTH ) )
        height  = int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT ) )
        fourcc  = cv2.VideoWriter_fourcc( 'm', 'p', '4', 'v' )
        out     = cv2.VideoWriter( self.text_file_name, fourcc, fps, ( width, height ) )

        self.pipe        = {'line0': False, 'line60': False, 'line120': False, 'line180': False, 'line240': True, 'line300': False, 'line360': False, 'line420': False, 'line480': False, 'line540': False, 'line600': False, 'line660': False}
        self.x           = []
        self.y           = [0] * 999
        self.text        = []
        self.cnt         = 0
        self.before_msec = 0

        while True:
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor( frame, cv2.COLOR_BGRA2RGB )
                pil_image = Image.fromarray( frame_rgb )
                msec = round( cap.get( cv2.CAP_PROP_POS_MSEC ) )
                draw = ImageDraw.Draw( pil_image )

                Subtitles.__draw_text( self, draw, width, msec )

                rgb_image = cv2.cvtColor( np.array( pil_image ), cv2.COLOR_RGB2BGR )
                out.write( rgb_image )
            else:
                break

        cap.release()
        out.release()

    def __draw_text( self, draw, width, msec ):
        font = ImageFont.truetype( 'custom/LightNovelPOP_FONT/lanovePOP.otf', 35 )

        if self.cnt == 0:
            self.before_msec = msec

        try:
            for s in range( self.before_msec, msec ):
                if s in self.comment.keys():
                    self.x.append( width + 200 )
                    #self.x.append( width )
                    #self.y.append( 0 )
                    self.text.append( self.comment[s] )
        except KeyError:
            pass

        self.before_msec = msec
        self.cnt += 1

        for i in range( len( self.x ) ):
            if not self.text[i] is None:
                #print( self.text[i] )
                text_len = ( ( len( self.text[i - 1] ) * 43 ) + self.x[i] )
                #text_len = ( ( len( self.text[i] ) ) + self.x[i] )
                for line in self.pipe:
                    if not self.pipe[line]:
                        self.pipe[line] = True
                        if self.y[i] == 0:
                            self.y[i] = int( line.split('e')[1] )
                            break
                    if text_len < width:
                        self.pipe[line] = False
                Subtitles.__set_font( draw, self.x[i], self.y[i], self.text[i], font, '#000000', 1 )
                draw.text( ( self.x[i], self.y[i] ), self.text[i], font = font, fill = ( 255, 255, 255, 125 ) )

                #x_move = 8 + ( len( self.text[i] ) / 5 ) # w : 13
                x_move = 6 + ( len( self.text[i] ) / 5 ) # w : 11
                self.x[i] -= x_move

                #if x_move <= 0:
                #文字が画面外にいくまでを求める
                #その数値と、次の文字の数値を比べて。
                #表示する列を決める
                #ランダムにパイプを割り振る　一番農工かも。。。

    def __progress( self, width, x_move ):
        #width = 1270
        width / x_move # w : 1270 / 11 = 115 count
        pass


    def create( self, sec, num ):
        self.text_file_name = self.dir + '/movie/' + num + '_clip_text_' + str( sec ) + '.mp4'
        if not os.path.exists( self.dir + "/movie/" + self.text_file_name ):
            pkl_comment_res = []
            with open( self.dir + "/comment.pkl", 'rb' ) as f:
                pkl_comment_res = pickle.load( f )
            #print( pkl_comment_res )

            start_msec = ( sec - 52 ) * 1000
            stop_msec  = ( sec + 63 ) * 1000

            self.comment = {}
            for i in range( len( pkl_comment_res ) ):
                try:
                    if start_msec <= pkl_comment_res[i]['time_msec'] <= stop_msec:
                        self.comment[pkl_comment_res[i]['time_msec'] - start_msec ] = pkl_comment_res[i]['text']
                except KeyError:
                    continue
            try:
                print( self.comment )
            except UnicodeEncodeError:
                pass

            Subtitles.__cv2_text( self, str( sec ), start_msec, num )
        else:
            print( "already put_text movie" )

#test
#sub = Subtitles( "Ocm6izV7FFA" )
#sub.create( 1877, "0" )
