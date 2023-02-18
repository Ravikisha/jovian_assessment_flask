from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required,logout_user,current_user
from dotenv import load_dotenv
from flask_login import UserMixin
load_dotenv()

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ravi:ukhKm1DjfUe8jvXmR4wmuR67dwJkg1iT@dpg-cfogbf2rrk0fd9osmejg-a.oregon-postgres.render.com/todolist_ibja'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    
    def __repr__(self) -> str:
        return f"{self.id} - {self.name} - {self.email}"
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    description = db.Column(db.String(1000))
    status = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self) -> str:
        return f"{self.id} - {self.title} - {self.description}"

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('register.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')
    
    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
    if user:
        flash('Email address already exists')
        return redirect(url_for('signup'))
    
    if password != confirm_password:
        flash('Passwords do not match')
        return redirect(url_for('signup'))
    else:
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully')
        return redirect(url_for('login'))


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    print(email, password)
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))
    login_user(user, remember=True)
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html',user=current_user, tasks=tasks)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Tasks routes
@app.route('/tasks', methods=['POST'])
@login_required
def addTask():
    title = request.form.get('task-title')
    description = request.form.get('task-desc')
    new_task = Task(title=title, description=description, user_id=current_user.id,status='created')
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/delete')
@login_required
def deleteTask(task_id):
    task = Task.query.filter_by(id=task_id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/update')
@login_required
def updateTask(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if task.status == 'created':
        task.status = 'completed'
    else:
        task.status = 'created'
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/clear')
@login_required
def clearTasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    for task in tasks:
        db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)