# coding: utf-8
import sqlite3


class DBConnect:

    def __init__( self, livers ):
        self.livers = livers

    def liver_info( self ):
        con = sqlite3.connect( 'custom/v_list.sqlite3' )
        cur = con.cursor()

        result_info = []

        for i in self.livers:
            sql = "SELECT name, ch_id, twitter_id FROM list WHERE name = \'" + i + "\'"
            print( sql )
            cur.execute( sql )
            rows = cur.fetchall()
            for row in rows:
                info = row[0] + "◆https://www.youtube.com/channel/" + row[1] + "\nTwitter◆" + row[2] +"\n\n"
                result_info.append( info )

        if not len( self.livers ) == len( result_info ):
            print('検索数が一致しません。')
            print( result_info )
            return "0"

        con.commit()
        con.close()

        return result_info

    def info( self ):
        con = sqlite3.connect( 'custom/v_list.sqlite3' )
        cur = con.cursor()

        result = []

        sql = "SELECT ch_id FROM list"
        cur.execute( sql )
        rows = cur.fetchall()
        for row in rows:
            info = "https://www.youtube.com/channel/" + row[0] + "?sub_confirmation=1"
            result.append( info )
        print( result )

        return result

    #mqlite3にライバー情報を追加
    def add_info( self ):
        con = sqlite3.connect( 'custom/v_list.sqlite3' )
        cur = con.cursor()

        sql = "insert into list( name, ch_id, twitter_id ) values ( 'ふぇありす', 'https://www.youtube.com/channel/UC2Rr7mILebYLTjd38DNNUTw', 'https://twitter.com/fairyschan' )"
        cur.execute( sql )

        con.commit()
        con.close()

    def add_col( self ):
        con = sqlite3.connect( 'custom/v_list.sqlite3' )
        cur = con.cursor()

        sql = "ALTER TABLE list ADD COLUMN hurigana TEXT"
        cur.execute( sql )

        con.commit()
        con.close()

    def add_hurigana( self, liver, kanzi ):
        con = sqlite3.connect( r'C:\Users\Ballista\Desktop/auto_kusa_clip\custom/v_list.sqlite3' )
        cur = con.cursor()

        sql = "update list set hurigana = \'" + liver + "\' where name = \'" + kanzi + "\'"
        cur.execute( sql )

        con.commit()
        con.close()


    def beautiful_s( self ):
        huri  = []
        kanzi = []
        res = requests.get( 'https://nijisanji.ichikara.co.jp/member/' )
        list = BeautifulSoup( res.text, 'html.parser' )
        #print( list.find( class_ = "insideline" ).find( "a" ).attrs['href'] )
        for i in list.find_all( class_ = "insideline" ):
            #print( i.find( "a" ).attrs['href'] )
            res = requests.get( i.find( "a" ).attrs['href'] )
            lists = BeautifulSoup( res.text, 'html.parser' )
            #print( lists.find_all( class_ = "elementor-heading-title elementor-size-default" )[1].text )
            for x in lists.find_all( class_ = "elementor-heading-title elementor-size-default" )[1]:
                #print( x.split( "/" )[0] )
                huri.append( x.split( "/" )[0] )
            for x in lists.find_all( class_ = "elementor-heading-title elementor-size-default" )[0]:
                #print( x )
                kanzi.append( x )

        for h, j in zip( huri, kanzi ):
            print( h, j )
            #DBConnect.add_hurigana( self, h, j )


    def get_info( self ):
        con = sqlite3.connect( 'custom/v_list.sqlite3' )
        cur = con.cursor()

        sql = "select ch_id, ch_name from list"
        cur.execute( sql )
        rows = cur.fetchall()
        for row in rows:
            print( row )

        con.commit()
        con.close()

#d = DBConnect(['葛葉', '叶'])
#d.beautiful_s()
#d.add_col()
#d.info()
#d.get_info()

#self = DBConnect( ['葛葉'] )
#print( self.liver_info() )

#c.execute('create table list(id integer primary key, name text, birthda)')
#c.execute("insert into list values (1, '太郎','B')")

#print( liver_info_sqlite(  ['葛葉', '叶', 'リゼ・ヘルエスタ', 'アンジュ・カトリーナ', '笹木咲', '椎名唯華', '天開司', 'ふぇありす'] ) )


#li = liver_info( ['葛葉','叶','一ノ瀬うるは'] )
#livers_des = ""
#for i in li:
#    livers_des += i

#livers = ['葛葉', '叶', '笹木咲', '椎名唯華', '魔界ノりりむ', '赤羽葉子', '本間ひまわり']
#print( "【にじさんじ : " + '/'.join(livers) + "】" )
