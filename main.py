import os
import webapp2
import jinja2

from signup import WelcomeHandler, SignUpPage

from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


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


#>>>>>>>>>>>>>>>>>>>>>>>>>DATABASE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

class Blog_DB(db.Model):
  blog_title = db.StringProperty(required=True) 
  blog_entry = db.TextProperty(required = True)
  created=db.DateTimeProperty(auto_now_add = True) 

#To define an 'entity'(table) in App Engine, you define a class. This is the database for blog entries.

#>>>>>>>>>>>>>>>>>>>>>>>>>>FRONT PAGE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class FrontPage(Handler):
  def render_front(self, blog_title="", blog_entry="", created=""):
      entries = db.GqlQuery("SELECT * FROM Blog_DB " 
                            "ORDER BY created DESC "
                            "LIMIT 10")
      
      self.render('frontpage.html', entries = entries)

  def get(self):
      self.render_front()


#>>>>>>>>>>>>>>>>>>>>>>>>>>NEW POST PAGE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class NewPost(Handler):
  def render_front(self, blog_title = "", blog_entry = "", error = ""):
###As NewPost is currently the root handler(change when we make main page?), this renders the front page by linking to the html template.
###blog_entry etc. are blank to start with but will change as the user submits posts.

      self.render('newpost.html')
      
      
  def get(self):
      self.render_front()
#1st get request: asking us to render the NewPost page.

  def post(self):
      blog_title = self.request.get("subject")
      blog_entry = self.request.get("content")
#Post request: when form is submitted, it will pull throught the title and the entry name from the {{variables}} in HTML.
       
    
      if blog_title and blog_entry:
          blog_post = Blog_DB(blog_title = blog_title, blog_entry = blog_entry)
          blog_post.put()
      
          blog_id = str(blog_post.key().id())
          self.redirect("/blog/%s" % blog_id)
      else:        
        error = 'We need both a Title and an Entry, Im Afraid'
        self.render_front(blog_title, blog_entry, error)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>PERMA LINK PAGE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class PermaLink(Handler):


  def get(self, perm_id):
      p = Blog_DB.get_by_id(int(perm_id))
      if p:
        self.render('permalink.html', p = p)
      else:
        self.error(404)
        return
        
                
        


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>QUERY PAGE>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class TestPage(FrontPage):
  def get(self):
      entries = db.GqlQuery("SELECT * FROM Blog_DB WHERE __KEY__ = KEY(Blog_DB', 5910974510923776)")
      
      self.render('testpage.html', entries = entries)

app = webapp2.WSGIApplication([
    ('/', FrontPage),
    ('/newpost', NewPost),
    ('/blog/(\d+)', PermaLink),
    ('/testpage', TestPage),
    ('/signup', SignUpPage),
    ('/welcome', WelcomeHandler)
], debug=True)
