import os
import webapp2
import jinja2
import cgi
import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PW_RE = re.compile(r"^.{3,20}$")
EM_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

tmplate_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(tmplate_dir),
                               autoescape = True)

def render_str(template, **params):
    temp = jinja_env.get_template(template)
    return temp.render(params)

def escape_html(s):
    return cgi.escape(s, quote = True)

def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PW_RE.match(password)

def valid_email(email):
    return not email or EM_RE.match(email)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))


class SignUp(BaseHandler):

    def get(self):
        self.render("signup-form.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        have_error = False
        tmp_kargs = {'username': username, 'email': email}

        if not valid_username(username):
            have_error = True
            tmp_kargs['error_username'] = 'Invalid username!!'

        if not valid_password(password):
            have_error = True
            tmp_kargs['error_password'] = 'Invalid password!!'
        elif password != verify:
            have_error = True
            tmp_kargs['error_verify'] = 'Different password!!'

        if not valid_email(email):
            have_error = True
            tmp_kargs['error_email'] = 'Invalid email!!'
            

        if have_error:
            self.render("signup-form.html", **tmp_kargs)
        else:
            self.redirect("/thanks?username=%s" % username)

class ThanksHandler(BaseHandler):
        def get(self):
            username = self.request.get('username')
            self.response.out.write("Welcome %s" % username)

app = webapp2.WSGIApplication([
    #('/', MainPage),
    ('/SignUp', SignUp),
    ('/thanks', ThanksHandler)
], debug=True)
