# coding: utf-8
from gensim.models import KeyedVectors

wv = KeyedVectors.load_word2vec_format( './live_chat_s.model', binary = True )
#results = wv.most_similar( positive = ["叶", "葛葉"], negative = [""], topn = 10 )
results = wv.most_similar( positive = ["御伽原江良"], topn = 50 )
for result in results:
    print( result )

#res = wv.rank("アンジュ", "リゼ")
#print( res )

#res = wv.get_vector( "アンジュ" )
#print( res )

#res = wv.distance("アンジュ", "リゼ")
#print( res )
