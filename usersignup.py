import webapp2
import cgi
import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PW_RE = re.compile(r"^.{3,20}$")
EM_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def escape_html(s):
    return cgi.escape(s, quote = True)

def valid_username(username):
    return USER_RE.match(username)

def valid_password(password):
    return PW_RE.match(password)

def valid_email(email):
    return EM_RE.match(email)

form="""
<form method="post">
    Sign up for now!
    <br>
    <label> Username
        <input type="text" name="username" value="%(username)s">
        <div style="color: red">%(err_username)s</div>
    </label>
    <br>

    <label> Password
        <input type="password" name="password">
        <div style="color: red">%(err_password)s</div>
    </label>
    <br>

    <label> Verify Password
        <input type="password" name="verify">
        <div style="color: red">%(err_verify)s</div>
    </label>
    <br>

    <label> Email address (optional)
        <input type="text" name="email" value="%(email)s">
        <div style="color: red">%(err_email)s</div>
    </label>


    <br>
    <br>
    <input type="submit">
</form>
"""

class MainPage(webapp2.RequestHandler):
    def write_form(self, username="", email="", 
                   err_username="", err_password="", err_verify="", err_email=""):
        self.response.out.write(form % {"username": escape_html(username),
                                        "email": escape_html(email),
                                        "err_username": escape_html(err_username),
                                        "err_password": escape_html(err_password),
                                        "err_verify": escape_html(err_verify),
                                        "err_email": escape_html(err_email)})
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        self.write_form()

    def post(self):
        user_name = self.request.get('username')
        user_password = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')

        name = valid_username(user_name)
        password = valid_password(user_password)
        verify = valid_password(user_verify)
        email = valid_email(user_email)

        err_u = ''
        err_p = ''
        err_v = ''
        err_e = ''

        if not (name and password and verify and (not user_email or email) and 
               (password.string == verify.string)):
            if not name:
                err_u = "That's not a valid username"
            if not password:
                err_p = "That wasn't a valid password"
            if password and verify:
                if password.string == verify.string:
                    pass
                else:
                    err_v = "different password!" 
            else:
                err_v = "different password!" 
            if user_email:
                if not email:
                    err_e = "That wasn't a valid email"

            self.write_form(user_name, user_email,
                            err_u, err_p, err_v, err_e)

        else:
            self.redirect("/thanks"+"?username=%s"%user_name)

class ThanksHandler(webapp2.RequestHandler):
        def get(self):
            user_name = self.request.get('username')
            self.response.out.write("Hi, %s"%user_name)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/thanks', ThanksHandler)
], debug=True)
