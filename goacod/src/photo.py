from google.appengine.api import users
from oauth2client.appengine import OAuth2Decorator
import auth
import base64
import httplib2
import json
import webapp2

# For all user and user alias operations, use this global user scope
SCOPE_USER = 'https://www.googleapis.com/auth/admin.directory.user'

# Use to limit the administrator's scope for retrieving users or user aliases
SCOPE_USER_READ = 'https://www.googleapis.com/auth/admin.directory.user.readonly'

SCOPES = [SCOPE_USER]

oauth2_decorator = OAuth2Decorator(
    client_id=auth.OAUTH_CONSUMER_KEY,
    client_secret=auth.OAUTH_CONSUMER_SECRET,
    scope=SCOPES,
    callback_path='/oauth2callback')

class Photo(webapp2.RequestHandler):
    @oauth2_decorator.oauth_required
    def get(self):
        user = users.get_current_user()
        email = user.email()
        if not email:
            self.response.out.write('no email found')
            return
        url = 'https://www.googleapis.com/admin/directory/v1/users/%s/photos/thumbnail' % email
        
        http = httplib2.Http()
        oauth2_decorator.credentials.authorize(http)
        
        response, content = http.request(url)
        if response.status == 200:
            data = json.loads(content)
            
            img = base64.urlsafe_b64decode(str(data['photoData']))
            #self.response.out.write('<img src="' + img +'" + alt="Lee Bailey" />')
            self.response.headers['content-type'] = str(data['mimeType'])
            self.response.out.write(img)
        else:
            # something went wrong
            self.abort(response.status)