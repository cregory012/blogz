from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy 


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

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

@app.route("/login", methods = ['POST', "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if user and user.password == password:
            # TODO remember that user logged in
            return redirect("/newpost")
        else:
            # TODO tell them why login failed
            return '<h1>Error</h1>'  


    return render_template("login.html")

@app.route("/signup", methods = ['POST', "GET"])
def signup():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form['password']
        verify = request.form["verify"]
        # TODO validate: password and verify

        existing_user = User.query.filter_by(username = username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            # TODO remember the user
            return redirect("/newpost")
        else:
            # TODO message that the username is taken
            return '<h1>Duplicate username</h1>'    

    return render_template("signup.html")    

@app.route('/blog')
def blog():

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