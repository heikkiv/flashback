import os.path
import ConfigParser

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

# Copy your credentials from the console
CLIENT_ID = config.get('default', 'google_app_client_id')
CLIENT_SECRET = config.get('default', 'google_app_client_secret')

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

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
