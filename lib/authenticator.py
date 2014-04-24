import pprint
import os.path

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import OAuth2Credentials
from oauth2client.file import Storage


# Copy your credentials from the console
CLIENT_ID = '20665032451-75qbcpnal2g8oel0f2a4r1emim4c70u0.apps.googleusercontent.com'
CLIENT_SECRET = '8RhsozdbXAA_yQRynmVoOnhR'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Path to the file to upload
FILENAME = '.credentials'


def get_credentials():
    storage = Storage(FILENAME)
    if os.path.isfile(FILENAME):
        credentials = storage.get()
    else:
        # Run through the OAuth flow and retrieve credentials
        flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        print 'Go to the following link in your browser: ' + authorize_url
        code = raw_input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)
        storage.put(credentials)

    return credentials
