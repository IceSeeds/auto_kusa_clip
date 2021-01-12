
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


def count_result( target_url ):
        youtube_select_url = 'https://www.youtube.com/watch?v=' + target_url + "&feature=youtu.be&t="
        res_comment = get_chat_replay_data( target_url )

        if len( res_comment ) != 0:
            with open( "analysis/" + target_url + "/comment.pkl", "wb" ) as f:
                pickle.dump( res_comment, f )

        return res_comment

def count_function( target_url ):
    dir = "analysis/" + target_url
    if not os.path.exists( dir ):#ディレクトリがなかったら
        os.makedirs( dir )

    pkl_comment_name = "video/clip/" + target_url + "/comment.pkl"
    pkl_comment_res     = []

    #ファイルの存在確認
    if not os.path.exists( pkl_comment_name ):
        res_comment = count_result( target_url )
    else:
        #ファイルサイズの確認
        if os.path.getsize( pkl_comment_name ) <= 100:
            res_comment = count_result( target_url )
        else:
            with open( pkl_comment_name, 'rb' ) as f:
                pkl_comment_res = pickle.load( f )
                res_comment = pkl_comment_res

    #print( count )
    return res_comment


count_function( 'tmlGY5rNQes' )
