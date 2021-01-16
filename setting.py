# coding: utf-8
import os
import time

from multiprocessing import Process, Queue, Pool
import pathlib
from playsound import playsound

from custom import cmd
from custom import line_send as line
from custom import db_connect as db
from lib import download_movie as dl
import kusa_counter #最後
from lib import clip
from lib import join
from lib import text_image
from lib import text_movie
from lib import image_to_video as img_to_video
from custom.upload import movie, image


#動画DL
def videodl( q, target_url ):
    self      = dl.VideoDL( target_url ) #動画のダウンロード処理
    v_path    = self.video_dl()
    q.put( v_path )
    return

#コメント解析
def analysis( q2, target_url ):
    c_count = kusa_counter.count_function( target_url, True )
    q2.put( c_count )
    return

def set_upload( target_url, livers, com_cnt, video_path ):
    result_video_id = None
    get_livers_info = False

    title = "【にじさんじ : " + '/'.join(livers) + "】"

    livers_link = ""

    self = db.DBConnect( livers )
    livers_info = self.liver_info()
    if not livers_info == "0":
        get_livers_info = True
        for i in livers_info:
            livers_link += i

    me_start_comment    = "\nコメント追加テスト。\n文字が重なってるところがある。。。\n\n自動2分切り抜き！\n\n\n"
    me_end_com          = "この切り抜きでの順位は、コメントでの「草」や「ｗ」などを計測して出した順位です。\n続きが気になる方は、上のリンクからアーカイブをご視聴下さい。"

    if get_livers_info:
        up_file     = "video/clip/" + target_url + "/end_out_" + target_url + ".mp4"
        up_title    = "【2分切り抜き】笑えるランキング" + title

        zoku_des    = "【続編】\n"
        for sec, cnt in zip( com_cnt, range( 3 ) ):
            zoku_des += "【第 " + str( cnt + 1 ) + " 位】\nhttps://youtu.be/" + target_url + "?t=" + str( com_cnt[cnt] ) + "\n"

        honp_des    = "\n【本編】\n" + video_path[1] + "\n" + video_path[0] + "\n\n"
        livers_des  = "【チャンネル】\n" + livers_link + "\n"
        up_des      = me_start_comment + zoku_des + honp_des + livers_des + me_end_com

        cmd.CMD(  os.path.basename(__file__), up_file + up_title + up_des )
        #result_video_id = upload.upload_function( up_file, up_title, up_des )
        result_video_id = movie.UploadMovie().upload_s( up_file, up_title, up_des )

    return result_video_id


def main( target_url ):
    start = time.perf_counter()
    #プロセス間のデータ受け渡しがキューかパイプでしかできない
    q  = Queue() #DLパス記録用のキュー
    q2 = Queue() #秒間コメント数記録用のキュー

    #並行処理
    pros  = Process( target = videodl,  args = ( q,  target_url ) ) #動画DL
    pros2 = Process( target = analysis, args = ( q2, target_url ) ) #コメント解析
    pros.start()
    pros2.start()

    video_path, sucsess = q.get()
    pros.join()
    comment_count, res, counts = q2.get()
    pros2.join()

    clip_result = ""

    #sucsess = False

    if sucsess and counts != 0 and not os.path.exists( "video/clip/" + target_url + "/end_out_" + target_url + ".mp4" ):
        img_create_self = text_image.ImageCreate( target_url, video_path[2], video_path[1] )
        img_video_self  = img_to_video.ImageToVideo( target_url )
        clip_self       = clip.Clip( target_url )
        text_movie_self = text_movie.Subtitles( target_url )

        print( comment_count )

        for i, num, count in zip( comment_count, range( 3 ), counts[0] ):
            #文字付きの画像を作成
            img_create_self.create( num + 1, str( count ), counts[1][0] )
            #動画を二分に切り抜く。( filepath, start_sec, stop_sec, youtube_url, sec, num )
            #clip_result = clip_self.movie( ( i - 70 ), ( i + 50 ), str( i ), str( num ) )
            clip_result = clip_self.movie( ( i - 60 ), ( i + 60 ), str( i ), str( num ) ) #ver 2.0
            #画像から、2分動画を繋げる３ｓの動画を作成
            img_video_self.movie( num )
            #切り抜いた動画にコメントを追加する。( youtube_url, sec, num )
            text_movie_self.create( i, str( num ) ) # 3235.585 seconds.

        #infoに動画情報を書き込む
        p_new = pathlib.Path( 'video/clip/' + target_url + '/info.txt' )
        with p_new.open( mode='w', encoding="utf-8" ) as f:
            for info in video_path:
                f.write( info + "\n" )

        #グラフ画像を12s動画にする。
        img_video_self.graph()

        #切り抜いた動画、音声を別々に結合する。
        join_self = join.Join( target_url )
        join_self.movie( comment_count )
        #別々に結合した動画、音声を、一つの動画に結合する。
        join_self.end_clip( "movie_out_" + target_url + ".mp4", "mp3_out_" + target_url + ".mp3", "end_out_" + target_url + ".mp4" )

        #確認用プリント
        #cmd.CMD( os.path.basename(__file__), video_path + comment_count + clip_result + "\n\n ALL SUCSESS" )

        print( "end" )
        playsound( "video/bgm/3s.mp3" )
        end = time.perf_counter()
        line.LineSend( target_url + " : Finish!" + f"実行時間: {end - start}" )
    else:
        cmd.CMD(  os.path.basename(__file__), str( sucsess ) + " : already end_out_file mp4" + " : count_ " + str( counts ) )
        end = time.perf_counter()
        line.LineSend( target_url + " : Finish!" + f"実行時間: {end - start}" )


    return comment_count, video_path, counts

if __name__ == '__main__':
    target_url = '2qwVzZkulIA'
    b_upload = True

    comment_count, video_path, count = main( target_url )

    if b_upload:
        print( "upload Run : " + str( b_upload ) )
        #1.出演しているライバーを入力
        livers = ["アルス・アルマル"]

        video_id = set_upload( target_url, livers, comment_count, video_path )

        image_url = 'video\clip/' + target_url + '\image/thumbnail_' + target_url + '.png'
        if video_id is not None:
            image.UploadImage().upload_s( video_id, image_url )
        else:
            print( "upload video id is None" )
    else:
        print( "upload Run : " + str( b_upload ) )

    #みんなで作る面白ランキング
    #コメントの重なりを防ぐ。詳細は lib/image_text.py
    #一週間のにじさんじ全員の動画のラインキング1位だけ動画を作る
