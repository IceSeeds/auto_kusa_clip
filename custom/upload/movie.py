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

class UploadMovie:

    def __init__( self ):
        httplib2.RETRIES = 1
        self.MAX_RETRIES = 10
        self.RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error,
                                IOError,
                                http.client.NotConnected,
                                http.client.IncompleteRead,
                                http.client.ImproperConnectionState,
                                http.client.CannotSendRequest,
                                http.client.CannotSendHeader,
                                http.client.ResponseNotReady,
                                http.client.BadStatusLine)
        self.RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
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


        self.VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


    def get_authenticated_service( self, args ):
        flow = flow_from_clientsecrets( self.CLIENT_SECRETS_FILE,
                                       scope=self.YOUTUBE_UPLOAD_SCOPE,
                                       message=self.MISSING_CLIENT_SECRETS_MESSAGE)

        #storage = Storage("%s-oauth2.json" % sys.argv[0])
        storage = Storage( "C:\\Users\\Ballista\\Desktop\\auto_kusa_clip\\custom\\upload\\setting.py-oauth2.json" )
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, args)

        return build(self.YOUTUBE_API_SERVICE_NAME,
                     self.YOUTUBE_API_VERSION,
                     http=credentials.authorize(httplib2.Http()))

    def initialize_upload( self, youtube, options ):
        tags = None
        if options.keywords:
            tags = options.keywords.split(",")

        body = dict(
            snippet=dict(
                title=options.title,
                description=options.description,
                tags=tags
            ),
            status=dict(
                privacyStatus=options.privacyStatus
            )
        )

        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
        )

        result = UploadMovie.resumable_upload( self, insert_request)

        return result


    def resumable_upload( self, insert_request):
        response = None
        error = None
        retry = 0

        result = ""

        while response is None:
            try:
                print("Uploading file...")  # print文
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print("Video id '%s' was successfully uploaded." % response['id'])
                        result = response['id']
                    else:
                        exit("The upload failed with an unexpected response: %s" % response)
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" % \
                            (e.resp.status, e.content)
                else:
                    raise
            except self.RETRIABLE_EXCEPTIONS as e:
                error = "A retriable error occurred: %s" % e
            if error is not None:
                print(error)
                retry += 1
                if retry > self.MAX_RETRIES:
                  exit("No longer attempting to retry.")
                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print("Sleeping %f seconds and then retrying..." % sleep_seconds)
                time.sleep(sleep_seconds)

        return result

    def upload_s( self, files, title, des ):
        argparser.add_argument("--file", help="Video file to upload", default = files, action='append', nargs='+' )
        argparser.add_argument("--title", help="Video title", default = title, action='append', nargs='+' )
        argparser.add_argument("--description",
                               help="Video description",
                               default = des, action='append', nargs='+' )
        argparser.add_argument("--keywords", help="Video keywords, comma separated",
                               default="", action='append', nargs='+')
        argparser.add_argument("--privacyStatus", choices=self.VALID_PRIVACY_STATUSES,
                               default=self.VALID_PRIVACY_STATUSES[1],
                               help="Video privacy status.", action='append', nargs='+')
        args = argparser.parse_args()

        if not os.path.exists(args.file):
            exit("Please specify a valid file using the --file= parameter.")

        youtube = UploadMovie.get_authenticated_service( self, args )
        try:
            result = UploadMovie.initialize_upload( self, youtube, args )
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

        return result
        #upload_function( "video/clip/EgsFTHKiqoo/1_endMovie_EgsFTHKiqoo_2164.mp4", "test titlesss", "desss" )
