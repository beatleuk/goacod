from google.appengine.api import urlfetch, users
from oauth2client.appengine import OAuth2Decorator
import auth
import base64
import httplib2
import jinja2
import json
import os
import webapp2

# For all user and user alias operations, use this global user scope
SCOPE_USER = 'https://www.googleapis.com/auth/admin.directory.user'

# Use to limit the administrator's scope for retrieving users or user aliases
SCOPE_USER_READ = 'https://www.googleapis.com/auth/admin.directory.user.readonly'

SCOPES = [SCOPE_USER_READ]

oauth2_decorator = OAuth2Decorator(
    client_id=auth.OAUTH_CONSUMER_KEY,
    client_secret=auth.OAUTH_CONSUMER_SECRET,
    scope=SCOPES,
    callback_path='/oauth2callback')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class Main(webapp2.RequestHandler):
    @oauth2_decorator.oauth_aware
    def get(self):
        user = users.get_current_user()
        html = """
        <h1>Admin SDK Example</h1>
        <p>Select an option:</p>
        <ul>
            <li><a href="/list_users">List All Users in Domain</a>
        </ul>
        <p><em>You will be asked to authenticate with your domain. Note that you must be a Google Apps Administrator for your domain for this app to work.</em></p>
        <hr />
        <p><em>Logged in as %s <a href="%s">Log Out</a></em></p>
        """ % (user.email(), users.create_logout_url('/'))
        
        if oauth2_decorator.has_credentials():
            html += '<a href=\'/revoke_token\'>Revoke OAuth2 Token</a>'
        
        self.response.out.write(html)

class ListUsers(webapp2.RequestHandler):
    @oauth2_decorator.oauth_required
    def get(self):
        user = users.get_current_user()
        domain = user.email().split('@')[1]
        email = user.email()
        url = 'https://www.googleapis.com/admin/directory/v1/users?domain=' + domain

        http = httplib2.Http()
        oauth2_decorator.credentials.authorize(http)
        
        response, content = http.request(url)
        if response.status == 200:
            domain_users = json.loads(content)['users']
            
            
            
            
            
            
            template_values = {
                'domain_users': domain_users,
                'email': email,                
            }
            
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))
                #out.write(img)
                #out.write('<img src="data:image/jpeg;base64,"' + photo_data +'" + alt="Lee Bailey" />')
                #self.response.out.write('</br>' + emails + '</p>')
            
        else:
            # something went wrong
            self.abort(response.status)


class RevokeToken(webapp2.RequestHandler):
    @oauth2_decorator.oauth_aware
    def get(self):
        if oauth2_decorator.has_credentials():
            access_token = oauth2_decorator.credentials.access_token
            url = 'https://accounts.google.com/o/oauth2/revoke?token=' + access_token
            urlfetch.fetch(url)
        self.redirect('/')

#&maxResults=max number of results per page
#&orderBy=email, givenName, or familyName
#&pageToken=token for next results page
#&query=email, givenName, or familyName:the query's value*
#&sortOrder=ascending or descending
#?domain=primary domain name

app = webapp2.WSGIApplication([
                               ('/oauth2callback', oauth2_decorator.callback_handler()),
                               ('/list_users', ListUsers),
                               ('/revoke_token', RevokeToken),
                               ('/.*', Main)
                               ])