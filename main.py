from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy 


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return  '<Title: {0}>'.format(self.title)   

@app.route('/blog')
def blog():

    blog_id_str = request.args.get('id')
    if blog_id_str:
        blog_id = int(blog_id_str)
        blog = Blog.query.get(blog_id)
        return render_template('display.html', title_html="Display Blog", blog=blog)

    blogs = Blog.query.all()
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