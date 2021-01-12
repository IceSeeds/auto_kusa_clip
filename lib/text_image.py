# coding: utf-8
import os
import shutil

import requests
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import numpy as np

class ImageCreate:

    def __init__( self, target_url, image_url, title ):
        self.target_url     = target_url
        self.dir            = "video/clip/" + self.target_url
        self.image_dir      = "video/clip/" + self.target_url + "/image"
        self.image_url      = image_url
        self.title          = title
        self.image_source   = self.image_dir + "/" + self.target_url + ".jpg"
        self.font_filename  = "custom/LightNovelPOP_FONT/ラノベPOP.otf"

    def __get_back_image( self ):
        #_1280, 720 = 100% = 100/100 = 1
        #_1024, 576 = 80% = 100/80   = 1.25
        back   = Image.open( "video/back.png" )#画像の読み込み
        source = Image.open( self.image_source )#画像の読み込み

        back_img = back.copy()
        back_img.paste( source )

        return back_img

    def __souce_create( self ):
        if not os.path.exists( self.image_dir + "/" + self.target_url + ".jpg" ):
            response    = requests.get( self.image_url )
            image       = response.content

            if not os.path.exists( self.image_dir ):#ディレクトリがなかったら
                os.makedirs( self.image_dir )

            with open( self.image_source, "wb" ) as wb:
                wb.write( image )

            img = Image.open( self.image_source )
            w, h = img.size
            if not w == 1024:
                print( w, h )
                re_size = img.resize( size = ( 1024, 576 ), resample = Image.NEAREST )
                re_size.save( self.image_source )
        else:
            print( "already image source" )

    def __thumbnail( self, count ):
        image_name = 'thumbnail_' + self.target_url + '.png'

        if not os.path.exists( self.image_dir + "/" + image_name ):
            img = ImageCreate.__get_back_image( self )
            draw = ImageDraw.Draw( img )

            width, height = img.size

            ImageCreate.__set_text( self, draw, width - 255, 10,  '草',  100, "#FFF" )
            ImageCreate.__set_text( self, draw, width - 190, 140, 'and', 60,  "#FFF" )
            ImageCreate.__set_text( self, draw, width - 90,  200, 'w',   100, "#FFF" )

            ImageCreate.__set_text( self, draw, width - 210, 385, '総計', 80, "#FFF", 5, "#800000" )

            ImageCreate.__set_count( self, draw, count, width, 480 )
            ImageCreate.__set_title( self, draw, width, height )

            img.save( self.image_dir + "/" + image_name ) #文字を挿入した画像を保存
        else:
            print( 'already image thumbnail' )

        return True

    def __set_text( self, draw, x, y, text, size, color, bold_size = None, bold_color = None ):
        font = ImageFont.truetype( self.font_filename, size ) #フォントの作成

        if not bold_size is None and not bold_color is None:
            draw.text( ( x - bold_size, y - bold_size ), text, font = font, fill = bold_color ) #文字列の挿入
            draw.text( ( x + bold_size, y - bold_size ), text, font = font, fill = bold_color ) #文字列の挿入
            draw.text( ( x + bold_size, y + bold_size ), text, font = font, fill = bold_color ) #文字列の挿入
            draw.text( ( x - bold_size, y + bold_size ), text, font = font, fill = bold_color ) #文字列の挿入

        draw.text( ( x, y ), text, font = font, fill = color ) #文字列の挿入

    def __set_count( self, draw, count, width, height ):
        if len( str( count ) ) <= 3:
            x_count = 160 + ( len( str( count ) ) * 30 )
            ImageCreate.__set_text( self, draw, width - x_count, height, str( count ) + ' コ', 75, "#FFF" )
        elif len( str( count ) ) >= 4:
            ImageCreate.__set_text( self, draw, width - 250, height, str( count ) + ' コ', 60, "#FFF" )

    def __set_title( self, draw, width, height ):
        sx, sy = 20   , height - 95
        ex, ey = width, height - 95
        length = ex - sx
        out_text_size = ( length + 1, height + 1 )
        font_size_offset = 0
        font = None

        while length < out_text_size[0]:
            font = ImageFont.truetype( self.font_filename, 150 - font_size_offset )
            out_text_size = draw.textsize( self.title, font = font )# draw.textsizeで描画時のサイズを取得
            font_size_offset += 1

        ImageCreate.__set_text( self, draw, sx, sy, self.title, 150 - font_size_offset, "#000", 4, "#FFF" )

    def create( self, num, count, all_count ):
        if num == 1:
            ImageCreate.__souce_create( self )
            ImageCreate.__thumbnail( self, all_count )

        image_name = str( num ) + '_image_' + self.target_url + '.png'
        if not os.path.exists( self.image_dir + "/" + image_name ):
            back_img = ImageCreate.__get_back_image( self )
            draw = ImageDraw.Draw( back_img )

            width, height = back_img.size

            ImageCreate.__set_text( self, draw, width - 235, 20, str( num ) + '位', 120, "#FFF", 8, "#800000" )
            ImageCreate.__set_text( self, draw, width - 190, 220, '草', 120, "#FFF" )

            ImageCreate.__set_count( self, draw, count, width, 420 )
            ImageCreate.__set_title( self, draw, width, height )

            back_img.save( self.image_dir + "/" + image_name, quality = 99 ) #文字を挿入した画像を保存
        else:
            print( 'already image_name created' )


#image = ImageCreate( "3hJPRYuteS4",
#                     "https://i.ytimg.com/vi/3hJPRYuteS4/maxresdefault.jpg?v=5fcfaff1",
#                     "＃56【Minecraft～にじ鯖～】雑談　 season2　【アルス・アルマル/にじさんじ】"
#                   )
#image.test( 1, "793" )
#image.create( 1, "99", "485" )
