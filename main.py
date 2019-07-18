from flask import Flask, redirect, request, render_template, session
from flask_sqlalchemy import SQLAlchemy 


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner  

    def __repr__(self):
        return  '<Title: {0}>'.format(self.title)

@app.before_request
def required_login():
    allowed_routes = ['login', 'signup', 'index', 'list_blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route("/login", methods = ['POST', "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect("/newpost")
        else:
            # TODO tell them why login failed
            return '<h1>Error</h1>'  


    return render_template("login.html")

def no_space(name):
     if name.count(" ") == 0:
          return True
     else:
          return False     

def right_length(name):
     if len(name) > 2 and len(name) < 21: 
          return True
     else:
          return False 
    

@app.route("/signup", methods = ['POST', "GET"])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        if not right_length(username) or not no_space(username):
            user_error = "That's not a valid username"
            username = ""
        else: 
            user_error = ''

        password = request.form['password']
        if not right_length(password) or not no_space(password):
            pass_error = "That's not a valid password"
        else:
            pass_error = ''

        verify = request.form['verify']
        if password != verify:
            verify_error = "Passwords don't match"
        else:
            verify_error = ''

        existing_user = User.query.filter_by(username = username).first()
        if existing_user:
            existence_error = "That username already exists"
            username = ''
        else:
            existence_error = ''    


        if user_error or pass_error or verify_error or existence_error:
            password = ""
            verify = ""
            return render_template("signup.html", username= username, password = password,
                verify = verify, user_error = user_error, pass_error = pass_error, 
                verify_error = verify_error, existence_error = existence_error)
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect("/newpost")

    return render_template("signup.html")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog')
def list_blogs():

    blog_id_str = request.args.get('id')
    if blog_id_str:
        blog_id = int(blog_id_str)
        blog = Blog.query.get(blog_id)
        return render_template('display.html', title_html="Display Blog", blog=blog)

    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', title_html="Build A Blog", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':

        title_error = ''
        body_error = ''

        blog_title = request.form['title']
        if blog_title == '':
            title_error = "Please fill in the title"
        else:
            title_error = ''

        blog_body = request.form['body']
        if blog_body == '':
            body_error = 'Please fill in the body'
        else:
            body_error = ''

        if  title_error or  body_error:
            return render_template('newpost.html', title_html="Add Blog Entry",
             title_error=title_error, body_error=body_error, title=blog_title, body=blog_body)
        else:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id="+ str(new_blog.id))

    return render_template('newpost.html', title_html="Add Blog Entry") 
    
if __name__ == '__main__':
    app.run() 