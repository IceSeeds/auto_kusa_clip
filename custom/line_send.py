# coding: utf-8
import requests

class LineSend:
    def __init__( self, notification_message ):
        self.message = notification_message
        LineSend.send( self )

    def send( self ):
        line_notify_token = 'mVZ91mHwvZS2X3QE6qXL1JbbMKJSn1pnSF2RVoCXHdS'
        line_notify_api = 'https://notify-api.line.me/api/notify'
        headers = { 'Authorization': f'Bearer {line_notify_token}' }
        data = { 'message': f'{self.message}' }
        requests.post( line_notify_api, headers = headers, data = data )

#LineSend( "testes" )
#line.send()
