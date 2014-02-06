import webapp2
import jinja2
import random
import string
import hashlib
import os
import re
import hmac

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> USER DATABASE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class User_DB(db.Model):
      db_user_name = db.StringProperty(required=True) 
      db_user_pass = db.StringProperty(required = True)
      db_user_email = db.StringProperty
      db_date_created=db.DateTimeProperty(auto_now_add = True) 
      

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> HASHING PROCEDURES <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
SECRET = 'secret'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
      return val
    return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>SALTING PROCEDURES<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
    if not salt:
      salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> HANDLER TEMPLATE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

class BlogHandler(webapp2.RequestHandler):
  def write(self, *a, **kw):
      self.response.out.write(*a, **kw)
###Defines function 'Write' which is a shortcut for self.response
      
  def render_str(self, template, **params):
      t = jinja_env.get_template(template)
      return t.render(params)
#     Function that takes a template name and returns a string of that rendered template
    
  def render(self, template, **kw):
      self.write(self.render_str(template, **kw))
#     Instead of just returning the string it calls 'Write' on it



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> REGULAR EXPRESSIONS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

PASS_RE = re.compile("^.{3,20}$")
def valid_password(password):
    return PASS_RE.match(password)


EMAIL_RE = re.compile("^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
    return EMAIL_RE.match(email)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> SIGN UP PAGE HANDLER <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

class SignUpPage(BlogHandler):      
    def get(self):
        self.render('signup.html')
#        self.write(check_secure_val('Bob|0cad8e636d2357b0bec1b62fc54d23fc'))
#        self.write(self.request.cookies.get('user_id'))


    def post(self):
        user_name = self.request.get('username')
        user_pass = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')
        
        hash_user_pass = make_pw_hash(user_name, user_pass)

        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>COOKIE VALIDATION<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        user_id = str(make_secure_val(user_name))   
#        self.response.headers.add_header('Set-Cookie', 'user_id=%s' % user_id)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
     

        user_error, pass_error, verify_error, email_error = "", "", "", ""
        
        if not valid_username(user_name):
            user_error = 'Invalid Username'

        elif not self.request.cookies.get('user_cookie_id'):
            self.response.headers.add_header('Set-Cookie', 'user_cookie_id=%s' % user_id)
            
        elif check_secure_val(self.request.cookies.get('user_cookie_id')) == False:
            self.redirect('http://www.google.com')
#        elif check_user_log('user_id') != 

        if  not valid_password(user_pass):
            pass_error = 'Invalid Password'
        
        elif user_pass != user_verify:
            verify_error = "Passwords Don't Match"

        if user_email:
            if not valid_email(user_email):  
                email_error = 'Invalid Email'
        else:
            email_error = ""
        
        self.render('signup.html', user_error = user_error,
                                   pass_error = pass_error,
                                   verify_error = verify_error,
                                   email_error = email_error)

        
    
    
    
    
    
        if not user_error and not pass_error and not verify_error and not email_error:
            user_profile = User_DB(db_user_name = user_name, db_user_pass = hash_user_pass, db_user_email = user_email) 
            user_profile.put()
            self.redirect("/blog/welcome")


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>LOGIN HANDLER<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class LoginPage(BlogHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        user_name = self.request.get('username')
        user_pass = self.request.get('password')

        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>COOKIE VALIDATION<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        user_id = str(make_secure_val(user_name))        
        self.response.headers.add_header('Set-Cookie', 'user_id=%s' % user_id)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

        login_error, user_exist_error = "", ""
        
        if not valid_username(user_name) or not valid_password(user_pass):
            login_error = 'Invalid login' 
          
        if user_name == self.request.cookies.get('user_id'):
            user_exist_error = 'You are already logged in'
            

        self.render('login.html', login_error = login_error,
                                  user_exist_error = user_exist_error)


    
    
    
    
    
        if not login_error and not user_exist_error:
            self.redirect("/blog/welcome")
            

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>WELCOME HANDLER<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            
class WelcomePage(BlogHandler):
      def get(self):
          self.response.out.write('Welcome, ')# + self.request.cookies.get('user_id'))
