from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    all_users = User.query.all()
    return render_template('index.html', main_title='Blogz!', all_users=all_users)

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
                
        username_error = ''
        userexist_error = ''
        password_error = ''
        verify_error = ''

        if username == '' or len(username) < 3 or len(username) > 20 or ' ' in username:
            username_error = "That's not a vaild username"
        if password == '' or len(password) < 3 or len(password) > 20 or ' ' in password:
            password_error = "That's not a vaild password"
        if verify == '' or len(verify) < 3 or len(verify) > 20 or ' ' in verify:
            verify_error = "That's not a vaild password"
        elif password != verify:
            verify_error = "Passwords don't match"
        
        if not username_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()

            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username']=username
                return redirect('/newpost')
            else:
                userexist_error = "This user already exists."
        else:
            return render_template('signup.html', title='Signup', 
            username_error=username_error, 
            password_error=password_error,
            verify_error=verify_error,
            userexist_error=userexist_error,
            username=username)

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_error = ''
        login_password_error = ''

        user = User.query.filter_by(username=username).first()
        
        if not user:
            user_error = "That username does not exist."
        if user and check_pw_hash(password, user.password):
            session['username']=username
            return redirect('/newpost')
        else:
            login_password_error = "That's not a vaild password"
            return render_template('login.html',
            username=username,
            user_error=user_error, 
            login_password_error = login_password_error)

    return render_template('login.html')

@app.route('/blog', methods=['GET'])
def blogs():
    id = request.args.get('id')
    user = request.args.get('user')

    if id:
        blog=Blog.query.filter_by(id=id).first()
        user_id=blog.owner_id
        user=User.query.filter_by(id=user_id).first()
        return render_template('blog.html', main_title='Blogz!', blog=blog, user=user)
    if user:
        user=User.query.filter_by(username=user).first()
        user_id=user.id
        user_blogs=Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', main_title='Blogz!', user=user, user_blogs=user_blogs)
    blogs = Blog.query.all()
    all_users = User.query.all()
    return render_template('main_blog.html', main_title='Blogz!', blogs=blogs, all_users=all_users)

@app.route('/newpost', methods=['POST', 'GET'])
def new_entry():
    
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        title_error = ''
        body_error = ''

        if title == '':
            title_error = "Please fill in the title."
        if body == '':
            body_error = "Please fill in the body."
        
        
        if not title_error and not body_error:
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            id = int(new_blog.id)
            return redirect('/blog?id=%s' % id)
        else:
            return render_template('newpost.html', main_title='Blogz!',
            title_error=title_error,
            body_error=body_error,
            title=title,
            body=body)

    return render_template('newpost.html', main_title='Blogz!')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()