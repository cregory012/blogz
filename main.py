from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 
from models import User, Blog
from app import app, db


@app.before_request
def required_login():
    allowed_routes = ['login', 'signup', 'home', 'list_blogs']
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
            flash('Logged in')
            return redirect("/newpost")
        else:
            flash("User password incorrect, or user does not exist", 'error') 

    return render_template("login.html", title_html="Login")


def get_logged_in_user():
    return User.query.filter_by(username = session['username']).first()

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

    return render_template("signup.html", title_html="Signup")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog')
def list_blogs():

    blog_id_str = request.args.get('id')
    username_request = request.args.get("username")
    
    if blog_id_str:
        owner = User.query.filter_by(username = username_request).first()
        blog_id = int(blog_id_str)
        blog = Blog.query.get(blog_id)
        return render_template('singleUser.html', title_html="Blog", blog=blog)

    if username_request:
        single_owner = User.query.filter_by(username = username_request).first()
        blogs = Blog.query.filter_by(owner = single_owner).order_by(Blog.id.desc()).all()
        return render_template("blog.html", title_html = "User's Blogs", blogs = blogs)
        


    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', title_html="All Blogs", blogs=blogs)

@app.route("/")
def home():
    users = User.query.all()
    return render_template("index.html", title_html="Home", users = users)

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
            new_blog = Blog(blog_title, blog_body, get_logged_in_user())
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id="+ str(new_blog.id))

    return render_template('newpost.html', title_html="Add Blog Entry") 
    
if __name__ == '__main__':
    app.run() 