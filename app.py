from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Blog
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to a login route if needed

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('introduction_page'))

@app.route('/about')
def introduction_page():
    return render_template('about.html')

# Logout route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify(success=True)

# Profile page route, requires login
@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')

# Blog page route
@app.route('/blog')
def blog_page():
    return render_template('blog.html')

# Blog page route
@app.route('/references')
def references_page():
    return render_template('references.html')

# Get current user route
@app.route('/current_user')
def get_current_user():
    if current_user.is_authenticated:
        return jsonify(display_name=current_user.display_name)
    else:
        return jsonify(display_name=None)

# Map page route
@app.route('/map')
def map_page():
    return render_template('map.html')

# Blog operations
@app.route('/get_blogs')
def get_blogs():
    blogs = db.session.query(Blog, User).join(User, Blog.user_id == User.id).all()
    current_user_id = current_user.id if current_user.is_authenticated else None
    blogs_data = [{'id': blog.id, 'title': blog.title, 'content': blog.content, 'username': user.display_name, 'user_id': blog.user_id} for blog, user in blogs]

    return jsonify(blogs=blogs_data, current_user_id=current_user_id)

@app.route('/create_blog', methods=['POST'])
@login_required
def create_blog():
    data = request.get_json()
    new_blog = Blog(content=data['content'], user_id=current_user.id, title=data['title'])
    db.session.add(new_blog)
    db.session.commit()
    return jsonify(success=True)

@app.route('/edit_blog/<int:blog_id>', methods=['POST'])
@login_required
def edit_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.user_id != current_user.id:
        return jsonify(success=False), 403  # Forbidden if user doesn't own the blog

    data = request.get_json()

    blog.content = data['content']
    blog.title = data['title']

    db.session.commit()
    return jsonify(success=True)

@app.route('/delete_blog/<int:blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.user_id != current_user.id:
        return jsonify(success=False), 403  # Forbidden if user doesn't own the blog

    db.session.delete(blog)
    db.session.commit()
    return jsonify(success=True)

# User signup route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if User.query.filter_by(display_name=data['display_name']).first():
        return jsonify(success=False, message='Display name already exists')
    
    new_user = User(display_name=data['display_name'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(success=True)

# User login route (for modal login)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(display_name=data['display_name']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify(success=True)
    
    return jsonify(success=False)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()
    
    if data.get('display_name'):
        # Check if the new display name is already taken by another user
        if User.query.filter_by(display_name=data['display_name']).first() and data['display_name'] != current_user.display_name:
            return jsonify(success=False, message="Display name already exists")
        current_user.display_name = data['display_name']

    if data.get('password'):
        current_user.set_password(data['password'])  # Hash the new password

    db.session.commit()
    return jsonify(success=True)


# Check if user is logged in
@app.route('/check_login')
def check_login():
    return jsonify(logged_in=current_user.is_authenticated)

# Create the necessary tables if they don't exist yet
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
