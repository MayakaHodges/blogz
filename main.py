from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog4me@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET'])
def index():
    id = request.args.get('id')
    if id:
        blog=Blog.query.filter_by(id=id).first()
        return render_template('blog.html', main_title='Build a Blog!', blog=blog)
    blogs = Blog.query.all()
    return render_template('main_blog.html', main_title='Build a Blog!', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_entry():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        title_error = ''
        body_error = ''

        if title == '':
            title_error = "Please fill in the title."
        if body == "":
            body_error = "Please fill in the body."
        
        
        if not title_error and not body_error:
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            id = int(new_blog.id)
            return redirect('/blog?id=%s' % id)
        else:
            return render_template('newpost.html', main_title='Build a Blog!',
            title_error=title_error,
            body_error=body_error,
            title=title,
            body=body)

    return render_template('newpost.html', main_title='Build a Blog!')

if __name__ == '__main__':
    app.run()