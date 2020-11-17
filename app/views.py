from app import app
from flask import render_template
from flask import request
from flask import redirect
import redis
import json
from datetime import datetime

current_user_data = None
users_arr = []
db = redis.Redis(host='redis', port=6379, db=0)

@app.route('/')
def index():
    return render_template('index.html', user=current_user_data)


@app.route('/logout')
def logout():
    global current_user_data
    current_user_data = None
    return redirect('/')

@app.route('/login/<login_type>', methods=['post', 'get'])
def login(login_type):
    button_login_type = 'Sign In' if login_type == 'signin' else 'Sign up'
    global current_user_data
    if current_user_data is not None:
        return redirect('/')
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if login_type == 'signin':
            if db.get(username):
                user_data = json.loads(db.get(username))
                if user_data['password'] == password:
                    current_user_data = user_data
                    current_user_data['username'] = username
                    return redirect('/')
            else:
                message = 'Incorrect username or password.'
        elif login_type == 'signup':
            if db.get(username):
                message = 'User with such name already exist. You\'re late! Try another nickname.'
            else:
                user_data = {
                    'password': password,
                    'posts': [],
                }
                data = json.dumps(user_data)
                db.set(username, data)
                current_user_data = user_data
                current_user_data['username'] = username
                                
                db_users = db.get('users')
                if db_users is None:
                    db_users = []
                else:
                    db_users = json.loads(db_users)
                db_users.append(username)
                db.set('users', json.dumps(db_users))
                global users_arr
                users_arr = db_users
                
                return redirect('/')
    return render_template('login.html', message=message, login_type=button_login_type)

@app.route('/<username>/posts', methods=['get', 'post'])
def posts(username):
    isCurrentUser = (current_user_data is not None and username == current_user_data['username'])
    posts = []
    if db.get(str(username) + '_posts'):
        posts = json.loads(db.get(str(username) + '_posts'))
    if request.method == 'POST':
        new_post = {
            'title': request.form.get('title'),
            'text': request.form.get('text'),
            'creation_time': datetime.now().strftime("%d %B %Y, %H:%M")
        }
        posts.insert(0, new_post)
        db.set(username+'_posts', json.dumps(posts))
    return render_template('posts.html', username=username, posts=posts, isCurrentUser=isCurrentUser)

@app.route('/users')
def users():
    global users_arr
    return render_template('users.html', users=users_arr)
    
