import webapp2
import jinja2
import os
import re

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> HANDLER TEMPLATE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

class Handler(webapp2.RequestHandler):
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


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Sign Up Page Handler <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

class SignUpPage(Handler):
      
    def get(self):
        self.render('signup.html')
        
    def post(self):
        user_name = self.request.get('username')
        user_pass = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')


        user_error, pass_error, verify_error, email_error = "", "", "", ""
        
        if not valid_username(user_name):
            user_error = 'Invalid Username'
            
        if not valid_password(user_pass):
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
            self.redirect("/welcome?username=" + user_name)
            

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>WELCOME HANDLER<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            
class WelcomeHandler(Handler):
      def get(self):
          user = self.request.get("username")
          self.response.out.write('Welcome, ' + user)
