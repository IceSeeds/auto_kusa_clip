import http.client  # httplibはPython3はhttp.clientへ移行
import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

class UploadImage:
    def __init__( self ):
        httplib2.RETRIES = 1
        self.CLIENT_SECRETS_FILE = "custom/upload/client_secrets.json"
        self.MISSING_CLIENT_SECRETS_MESSAGE = """
        WARNING: Please configure OAuth 2.0

        To make this sample run you will need to populate the client_secrets.json file
        found at:

           %s

        with information from the API Console
        https://console.developers.google.com/

        For more information about the client_secrets.json file format, please visit:
        https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
        """ % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           self.CLIENT_SECRETS_FILE))

        self.YOUTUBE_UPLOAD_SCOPE     = "https://www.googleapis.com/auth/youtube.upload"
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION      = "v3"


    def get_authenticated_service( self, args):
        flow = flow_from_clientsecrets(self.CLIENT_SECRETS_FILE,
                                       scope=self.YOUTUBE_UPLOAD_SCOPE,
                                       message=self.MISSING_CLIENT_SECRETS_MESSAGE)

        import os.path
        dirname = os.getcwd()
        #storage = Storage("custom/upload\%s-oauth2.json" % sys.argv[0])
        storage = Storage( dirname + "\\custom\\upload\\setting.py-oauth2.json" )
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, args)

        return build(self.YOUTUBE_API_SERVICE_NAME,
                     self.YOUTUBE_API_VERSION,
                     http=credentials.authorize(httplib2.Http()))

    def upload_thumbnail( self, youtube, video_id, file):
      youtube.thumbnails().set(
        videoId=video_id,
        media_body=file
      ).execute()

    def upload_s( self, videoid, files_thumbnail ):
        print( files_thumbnail )
        # The "videoid" option specifies the YouTube video ID that uniquely
        # identifies the video for which the thumbnail image is being updated.
        argparser.add_argument("--video-id", default = videoid )
        # The "file" option specifies the path to the thumbnail image file.
        argparser.add_argument("--file_thumbnail", default = files_thumbnail )
        args = argparser.parse_args()

        if not os.path.exists(args.file_thumbnail):
            exit("Please specify a valid file using the --file= parameter.")

        youtube = UploadImage.get_authenticated_service( self, args )
        try:
            UploadImage.upload_thumbnail( self, youtube, args.video_id, args.file_thumbnail)
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        else:
            print( "The custom thumbnail was successfully set." )

    #upload_image( 'kAvDTWYpN5M', 'video\clip\EgsFTHKiqoo\image/1_image_EgsFTHKiqoo.png' )
