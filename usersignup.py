import os
import webapp2
import jinja2
import cgi
import re
import hmac
import random
import string
import hashlib

from google.appengine.ext import db
tmplate_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(tmplate_dir),
                               autoescape = True)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PW_RE = re.compile(r"^.{3,20}$")
EM_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

SECRET = 'b99201001'

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt=make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)

def render_str(template, **params):
    temp = jinja_env.get_template(template)
    return temp.render(params)

def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PW_RE.match(password)

def valid_email(email):
    return not email or EM_RE.match(email)

class User(db.Model):
    username = db.StringProperty(required = True)
    hashpw = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class Rot13(BaseHandler):
    def get(self):
        self.render("rot13-form.html")

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')

        self.render('rot13-form.html', text = rot13)

def cookie_make(username):
    return '%s|%s' % (username, hmac.new(SECRET, username).hexdigest())

def cookie_check_user(cookie):
    val = cookie.split('|')[0]
    return val if cookie_make(val) == cookie else None

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
            tmp_kargs['error_username'] = 'Invalid username!'

        if not valid_password(password):
            have_error = True
            tmp_kargs['error_password'] = 'Invalid password!'
        elif password != verify:
            have_error = True
            tmp_kargs['error_verify'] = 'Different password!'

        if not valid_email(email):
            have_error = True
            tmp_kargs['error_email'] = 'Invalid email!'

        if have_error:
            self.render("signup-form.html", **tmp_kargs)
        else:
            hashpw = make_pw_hash(username, password)
            cookie = str(cookie_make(username))
            self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % cookie )
            print 'un', username, 'hp', hashpw
            a = User(username = username, hashpw = hashpw)
            a.put()
            self.redirect('/')

class LogIn(BaseHandler):
    def get(self):
        self.render("login-form.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        if username and password:
            u = User.all().filter('username =', username).get() 
            if u and valid_pw(username, password, u.hashpw):
                cookie = str(cookie_make(username))
                self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % cookie )
                self.redirect('/')
            else:
                error = 'invalid login'
                self.render("login-form.html", error=error)
        else:
            error = dict(username=username)
            if not username:
                error['error_username'] = 'please fillin username'
            if not password:
                error['error_password'] = 'please fillin password'
            self.render("login-form.html", **error)


class Welcome(BaseHandler):
    def get(self):
        username_cookie = self.request.cookies.get('username', 'None')
        if cookie_check_user(username_cookie):
            self.render('welcome.html', username = username_cookie.split('|')[0])
        else:
            self.redirect('/signup')

app = webapp2.WSGIApplication([
    ('/', Welcome),
    ('/signup', SignUp),
    ('/login', LogIn),
    ('/rot13', Rot13)
], debug=True)
