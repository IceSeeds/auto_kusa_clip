# coding: utf-8
import os
import pickle
import logging
import re
import MeCab

from gensim.models import word2vec
from gensim import *

from gensim.models import KeyedVectors

def mecab( text ):
    #t = MeCab.Tagger('-O wakati -u analysis/csv_2434.dic')
    t = MeCab.Tagger('-O wakati')
    sentence = text
    return t.parse(sentence)

def train_model():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    sentences = word2vec.Text8Corpus('analysis/live_wakati.txt')

    model = word2vec.Word2Vec( sentences, size = 200, min_count = 20, window = 15 )
    model.wv.save_word2vec_format( "analysis/live_chat_s.model", binary = True )

def get_text():
    wv = KeyedVectors.load_word2vec_format( 'analysis/live_chat_s.model', binary = True )
    results = wv.most_similar( positive = ["NISC"], topn = 10 )

    for result in results:
        print( result )

def main():
    youtube_video_id = "tmlGY5rNQes"
    pkl_comment_name = "analysis/" + youtube_video_id + "/comment.pkl"

    pkl_comment_res = []
    with open( pkl_comment_name, 'rb' ) as f:
        pkl_comment_res = pickle.load( f )

    text_data = ""
    for i in range( len( pkl_comment_res ) ):
        try:
            text_data += pkl_comment_res[i]['text']
        except KeyError:
            continue

    text_sub = re.sub('(「|」|？|!|！|@|＠|<|>|＜|＞|~|￥|＾|ー|＝|-|。|、|,|&|%|$|#|"|\'|）|（|_|＿)|【|】|『|』', '', text_data )
    text_mecab = mecab( text_sub )

    path_w = "analysis/live_wakati.txt"
    with open( path_w, mode = 'a', encoding = "utf-8" ) as f:
        f.write( text_mecab )

    train_model()

get_text()
#main()
