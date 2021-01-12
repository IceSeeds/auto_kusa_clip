# coding: utf-8
import datetime
import pickle

class CMD:
    def __init__( self, place, text ):
        self.place = place
        self.text  = text
        CMD.sys_print( self )

    def sys_print( self ):
        try:
            print( self.place +  " : " + str( self.text ) )
            file_name = "log/" + str( datetime.date.today() ) + "_print.log"
            with open( file_name, mode = "a", encoding="utf-8" ) as f:
                f.write( self.place +  " : " + str( self.text ) + "\n" )
        except UnicodeEncodeError:
            pass

    def get_pkl( self, pkl_name ):
        with open( pkl_name, 'rb' ) as f:
            result = pickle.load( f )
            print( result )

#CMD = CMD( "cmd", "text_cmd" )
#CMD.sys_print()
#CMD.get_pkl( "video\clip\KEqEGR0VlKY/sec.pkl" )
