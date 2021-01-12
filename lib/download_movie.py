# coding: utf-8
import os
import urllib

from pytube import YouTube

#from custom import cmd


class VideoDL:

    def __init__( self, target_url ):
            self.target_url = target_url
            self.link       = "https://www.youtube.com/watch?v=" + target_url
            self.dir        = "video/full"
            self.dl_name    = "clip_" + target_url

    def video_dl( self ):
            result = []
            youtube = YouTube( self.link )

            result.append( self.link )
            result.append( youtube.title )
            result.append( youtube.thumbnail_url )
            result.append( youtube.description )

            #cmd.CMD( os.path.basename(__file__), result )

            sucsess = True

            if( os.path.exists( self.dir + "/" + self.dl_name + ".mp4" ) ):
                #cmd.CMD( os.path.basename(__file__), 'already full_download created !!!' )
                return result, True
            else:
                itag_highest = 0

                available_list = YouTube( self.link ).streams
                itag_highest = str( available_list.get_highest_resolution() )[15:18]

                if itag_highest != 0:
                    if '\"' in itag_highest:
                        itag_highest = itag_highest[0:2]
                        sucsess = VideoDL.__try_dl( self, itag_highest )
                else:
                    pass
                    #cmd.CMD( os.path.basename(__file__), 'No download!!' )

            return result, sucsess

    def __try_dl( self, itag ):
            result = True
            for i in range( 3 ):
                try:
                    YouTube( self.link ).streams.get_by_itag( itag ).download( self.dir, self.dl_name )
                except urllib.error.HTTPError:
                    #cmd.CMD( os.path.basename(__file__), "HTTPError : " + str( i ) )
                    os.remove( 'video/full/clip_' + self.target_url + '.mp4' )
                    result = False
                    continue

            return result


#テスト用( 小森めと雑談　３０分 eCC00dsxZfI )
#videoDL = VideoDL( "aE1iMqZAu3g" )
#videoDL.video_dl()
