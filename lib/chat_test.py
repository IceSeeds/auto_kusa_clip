import os
import pickle

youtube_video_id = "tmlGY5rNQes"

pkl_count_name   = "video/clip/" + youtube_video_id + "/count.pkl"
pkl_sec_name     = "video/clip/" + youtube_video_id + "/sec.pkl"
pkl_comment_name = "video/clip/" + youtube_video_id + "/comment.pkl"

if not os.path.exists( pkl_count_name ) and not os.path.exists( pkl_sec_name ) and not os.path.exists( pkl_comment_name ):
    #result, res, count = count_result( youtube_video_id, image_save )
    print( 1 )
else:
    if( os.path.getsize( pkl_count_name ) <= 5 ) and os.path.getsize( pkl_sec_name ) <= 5 and os.path.getsize( pkl_comment_name ) <= 100:
        #result, res, count = count_result( youtube_video_id, image_save )
        print( 2 )
    else:
        with open( pkl_count_name, 'rb' ) as f:
            pkl_count_all_count = pickle.load( f )
            count = pkl_count_all_count
        with open( pkl_count_name, 'rb' ) as f:
            pkl_count_all_count = pickle.load( f )
            count = pkl_count_all_count
        with open( pkl_count_name, 'rb' ) as f:
            pkl_count_all_count = pickle.load( f )
            count = pkl_count_all_count
