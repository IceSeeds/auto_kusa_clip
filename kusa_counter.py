
import os
import re
import sys
import json
import shutil
import pickle
import time

import requests
from retry import retry
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

class ContinuationURLNotFound(Exception):
   pass

class LiveChatReplayDisabled(Exception):
   pass

def get_ytInitialData(target_url, session):
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
    html = session.get(target_url, headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')
    for script in soup.find_all('script'):
        script_text = str(script)
        if 'ytInitialData' in script_text:
            for line in script_text.splitlines():
                if 'ytInitialData' in line:
                    if 'var ytInitialData =' in line:
                        st = line.strip().find('var ytInitialData =') + 19
                        return(json.loads(line.strip()[st:-10]))
                    if 'window["ytInitialData"] =' in line:
                        return(json.loads(line.strip()[len('window["ytInitialData"] = '):-1]))

def get_continuation(ytInitialData):
   continuation = ytInitialData['continuationContents']['liveChatContinuation']['continuations'][0].get('liveChatReplayContinuationData', {}).get('continuation')
   return(continuation)

#チャットリプレイが無効な動画を検知
def check_livechat_replay_disable(ytInitialData):
   conversationBarRenderer = ytInitialData['contents']['twoColumnWatchNextResults']['conversationBar'].get('conversationBarRenderer', {})
   if conversationBarRenderer:
       if conversationBarRenderer['availabilityMessage']['messageRenderer']['text']['runs'][0]['text'] == 'この動画ではチャットのリプレイを利用できません。':
           return(True)


#
# get_chat_replay_data --- get_chat_replay_data( target_url, session )
# target_url = https://www.youtube.com/watch?v=video_id
#
@retry(ContinuationURLNotFound, tries=3, delay=1)
def get_initial_continuation(target_url,session):

   ytInitialData = get_ytInitialData(target_url, session)


   if check_livechat_replay_disable(ytInitialData):
       print("LiveChat Replay is disable")
       raise LiveChatReplayDisabled

   continue_dict = {}
   continuations = ytInitialData['contents']['twoColumnWatchNextResults']['conversationBar']['liveChatRenderer']['header']['liveChatHeaderRenderer']['viewSelector']['sortFilterSubMenuRenderer']['subMenuItems']


   for continuation in continuations:
       continue_dict[continuation['title']] = continuation['continuation']['reloadContinuationData']['continuation']

   continue_url = continue_dict.get('Live chat repalay')
   if not continue_url:
       continue_url = continue_dict.get('上位のチャットのリプレイ')

   if not continue_url:
       continue_url = continue_dict.get('チャットのリプレイ')

   if not continue_url:
       continue_url = ytInitialData["contents"]["twoColumnWatchNextResults"]["conversationBar"]["liveChatRenderer"]["continuations"][0].get("reloadContinuationData", {}).get("continuation")

   if not continue_url:
       raise ContinuationURLNotFound

   #print( "★★★★★★" + continue_url )
   return( continue_url )

def convert_chatreplay(renderer):
   chatlog = {}

   content = ""
   if 'message' in renderer:
       if 'simpleText' in renderer['message']:
           content = renderer['message']['simpleText']
       elif 'runs' in renderer['message']:
           for runs in renderer['message']['runs']:
               if 'text' in runs:
                   content += runs['text']

   chatlog['text'] = content

   return(chatlog)


#
#   main --- get_chat_replay_data( video_id )
#
def get_chat_replay_data(video_id):
   youtube_url = "https://www.youtube.com/watch?v="
   target_url = youtube_url + video_id
   continuation_prefix = "https://www.youtube.com/live_chat_replay?continuation="

   result = []
   session = requests.Session()
   continuation = ""

   try:
       continuation = get_initial_continuation(target_url, session)
   except LiveChatReplayDisabled:
       print(video_id + " is disabled Livechat replay")
       raise LiveChatReplayDisabled
   except ContinuationURLNotFound:
       print(video_id + " can not find continuation url")
       raise ContinuationURLNotFound
   except Exception:
       print("Unexpected error:ssssssssss" + str(sys.exc_info()[0]))

   count = 1
   while(1):
       if not continuation:
           break

       try:
           ytInitialData = get_ytInitialData(continuation_prefix + continuation, session)
           if not 'actions' in ytInitialData['continuationContents']['liveChatContinuation']:
               break
           for action in ytInitialData['continuationContents']['liveChatContinuation']['actions']:
               if not 'addChatItemAction' in action['replayChatItemAction']['actions'][0]:
                   continue
               chatlog = {}

               item = action['replayChatItemAction']['actions'][0]['addChatItemAction']['item']
               if 'liveChatTextMessageRenderer' in item:
                   chatlog = convert_chatreplay(item['liveChatTextMessageRenderer'])
                   #print(chatlog['text'])
               if not "" in chatlog:
                   time_msec = int(action["replayChatItemAction"]["videoOffsetTimeMsec"])#コメントした時間のミリ秒を取得
                   chatlog['time_msec'] = time_msec

                   time_sec = int( time_msec / 1000 )#ミリ秒→秒に変換
                   chatlog['time_sec']  = time_sec

               result.append(chatlog)

           continuation = get_continuation(ytInitialData)

       except requests.ConnectionError:
           print("Connection Error")
           continue
       except requests.HTTPError:
           print("HTTPError")
           break
       except requests.Timeout:
           print("Timeout")
           continue
       except requests.exceptions.RequestException as e:
           print(e)
           break
       except KeyError as e:
           print("KeyError")
           print(e)
           break
       except SyntaxError as e:
           print("SyntaxError")
           print(e)
           break
       except KeyboardInterrupt:
           break
       except Exception as e:
           print("Unexpected error:" + str(sys.exc_info()[0]))
           print(e)
           break

   return( result )

def graph_create( id, array_sec, array_kusa ):
    image_name = "video/clip/" + id + "/img_" + id + ".png"
    if not len( array_sec ) == 0:
        # グラフの描画先の準備
        fig = plt.figure()

        #グラフタイトル
        plt.title( 'kusa Graph' )

        #グラフの軸
        plt.xlabel( 'sec' )
        plt.ylabel( 'count' )

        # 折れ線グラフを出力
        left   = np.array( array_sec )
        height = np.array( array_kusa )
        plt.plot( left, height )

        # グラフをファイルに保存する
        fig.savefig( image_name )

        img = Image.open( image_name )
        re_size = img.resize( size = ( 1280, 720 ), resample = Image.NEAREST )
        re_size.save( image_name )

        return image_name
    else:
        return image_name


def count_result( target_url, image_save ):
        youtube_select_url = 'https://www.youtube.com/watch?v=' + target_url + "&feature=youtu.be&t="
        res_comment = get_chat_replay_data( target_url )

        array_sec    = []
        array_kusa   = []
        array_intar  = []
        kusa_cnt     = 0
        all_kusa_cnt = 0
        dic          = {}
        time_dic     = {}
        time         = 0
        time_start   = 0

        for i in range(len(res_comment)):
            if 'text' in res_comment[i].keys():
                if not "" in res_comment[i].values():
                    #if '草' in res[i]['text'] or 'w' in res[i]['text'] or '!?' in res[i]['text'] or '！？' in res[i]['text'] or '!!' in  res[i]['text'] or '笑' in res[i]['text']:
                    if '草' in res_comment[i]['text'] or 'w' in res_comment[i]['text'] or '笑' in res_comment[i]['text']:
                        if kusa_cnt == 0:
                            time_start = res_comment[i]['time_sec']

                        time = res_comment[i]['time_sec']
                        kusa_cnt += 1
                        all_kusa_cnt += 1

                    elif res_comment[i]['time_sec'] > ( time + 5 ):
                        array_sec.append(res_comment[i]['time_sec'])
                        array_kusa.append(kusa_cnt)
                        dic[kusa_cnt] = res_comment[i]['time_sec']

                        time_dic[kusa_cnt] = time - time_start
                        if time_start != 0:
                            array_intar.append( time_dic )

                        kusa_cnt = 0
                        time_start = 0

        print( sorted( time_dic.keys(), reverse=True )[0:3] )

        time_sec = []
        sec_d = sorted( dic.keys(), reverse=True )[0:3]
        for i in sec_d:
            tmp = dic[i] - time_dic.get( i )
            time_sec.append( tmp )
        #print( time_sec )

        counts = []
        count_data = sorted( array_kusa, reverse=True )[0:3]
        counts.append( count_data )
        counts.append( [all_kusa_cnt] )

        if image_save:
            graph_create( target_url, array_sec, array_kusa )

        if all_kusa_cnt != 0:
            with open( "video/clip/" + target_url + "/count.pkl", "wb" ) as f:
                pickle.dump( counts, f )
        if len( time_sec ) != 0:
            with open( "video/clip/" + target_url + "/sec.pkl", "wb" ) as f:
                pickle.dump( time_sec, f )
        if len( res_comment ) != 0:
            with open( "video/clip/" + target_url + "/comment.pkl", "wb" ) as f:
                pickle.dump( res_comment, f )

        return time_sec, res_comment, counts

def count_function( target_url, image_save ):
    dir = "video/clip/" + target_url
    if not os.path.exists( dir ):#ディレクトリがなかったら
        os.makedirs( dir )

    pkl_count_name   = "video/clip/" + target_url + "/count.pkl"
    pkl_sec_name     = "video/clip/" + target_url + "/sec.pkl"
    pkl_comment_name = "video/clip/" + target_url + "/comment.pkl"

    pkl_count_all_count = []
    pkl_sec_result      = []
    pkl_comment_res     = []

    #ファイルの存在確認
    if not os.path.exists( pkl_count_name ) and not os.path.exists( pkl_sec_name ) and not os.path.exists( pkl_comment_name ):
        time_sec, res_comment, count = count_result( target_url, image_save )
    else:
        #ファイルサイズの確認
        if( os.path.getsize( pkl_count_name ) <= 5 ) and os.path.getsize( pkl_sec_name ) <= 5 and os.path.getsize( pkl_comment_name ) <= 100:
            time_sec, res_comment, count = count_result( target_url, image_save )
        else:
            with open( pkl_count_name, 'rb' ) as f:
                pkl_count_all_count = pickle.load( f )
                count = pkl_count_all_count
            with open( pkl_sec_name, 'rb' ) as f:
                pkl_sec_result = pickle.load( f )
                time_sec = pkl_sec_result
            with open( pkl_comment_name, 'rb' ) as f:
                pkl_comment_res = pickle.load( f )
                res_comment = pkl_comment_res

    #print( count )
    return time_sec, res_comment, count


#count_function( 'tmlGY5rNQes', True )
