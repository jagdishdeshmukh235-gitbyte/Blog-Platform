from flask import Flask, render_template, request
from forms import RegisterForm
from models import db, User
from models import Post
from models import Comment
from flask import session

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db.init_app(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/register', methods=['GET','POST'])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        # check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            return "Email already registered. Please login."

        # create new user
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )

        db.session.add(new_user)
        db.session.commit()

        return "User Registered Successfully"

    return render_template("register.html", form=form)

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user'] = user.username 
            return "Login Successful"

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return "User Logged Out"

@app.route('/create', methods=['GET','POST'])
def create():

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        new_post = Post(title=title, content=content)

        db.session.add(new_post)
        db.session.commit()

        return render_template("success.html")

    return render_template("create_post.html")

@app.route('/posts')
def posts():
    all_posts = Post.query.all()
    return render_template("posts.html", posts=all_posts)

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):

    post = Post.query.get(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']

        db.session.commit()

        return "Post Updated"

    return render_template("create_post.html")

@app.route('/delete/<int:id>')
def delete(id):

    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()

    return "Post Deleted"

@app.route('/post/<int:id>', methods=['GET','POST'])
def post_detail(id):

    post = Post.query.get(id)
    comments = Comment.query.filter_by(post_id=id).all()

    if request.method == 'POST':

        if 'user' not in session:
            return "Please login first"

        content = request.form['content']

        new_comment = Comment(
            content=content,
            username=session['user'],
            post_id=id
        )

        db.session.add(new_comment)
        db.session.commit()

    return render_template("post_detail.html", post=post, comments=comments)

@app.route('/like/<int:id>')
def like(id):

    post = Post.query.get(id)
    post.likes += 1

    db.session.commit()

    return "Liked!"

if __name__ == '__main__':
    app.run(debug=True)