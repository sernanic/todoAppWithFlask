from flask import Flask, redirect, url_for, render_template, request
from models import db
from flask_bootstrap import  Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField
from wtforms.validators import InputRequired, Email,Length
from flask_sqlalchemy import SQLAlchemy
from models import User
from models import ToDO
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Flask
app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = '\x14B~^\x07\xe1\x197\xda\x18\xa6[[\x05\x03QVg\xce%\xb2<\x80\xa4\x00'
app.config['DEBUG'] = True
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/nicolasserna/Downloads/flask_project_default/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Forms 
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('home'))
        return '<h1>Invalid password or username</h1>' 
    return render_template("login.html",form = form)

@app.route("/signup",methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("signup.html",form = form)

@app.route("/home")
def home():
    if current_user.is_authenticated:
        todosComplete  = ToDO.query.filter_by(userId = current_user.id,complete = True).order_by(ToDO.dueDate).all()
        todosIncomplete  = ToDO.query.filter_by(userId = current_user.id,complete = False).order_by(ToDO.dueDate).all()
        return render_template("home.html",
        name = current_user.username,
        complete=todosComplete,incomplete = todosIncomplete,userId = current_user.id)
    else:
        return redirect(url_for('login'))


@app.route('/add', methods=['POST'])
def add():
    todo = ToDO(userId =current_user.id, text=request.form['todoitem'], complete=False,dueDate = request.form['dueDate'])
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/complete/<id>')
def complete(id):
    todo = ToDO.query.filter_by(id=int(id)).first()
    todo.complete = True
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/update/<int:id>',methods = ['GET','POST'])
def update(id):
    updateTodo = ToDO.query.filter_by(id = id).first()
    if request.method == 'POST':
        if updateTodo:
            db.session.delete(updateTodo)
            db.session.commit()
            updateText = request.form['updateText']
            updateDueDate = request.form['updateDueDate']
            updateTodo = ToDO(userId =current_user.id, text=updateText, complete=updateTodo.complete,dueDate = updateDueDate)
            db.session.add(updateTodo)
            db.session.commit()
            return redirect(url_for('home'))

@app.route('/delete/<int:id>', methods=['GET','POST'])
def delete(id):
    deleteTodo= ToDO.query.filter_by(id = id).first()
    if request.method == 'POST':
        if deleteTodo:
            db.session.delete(deleteTodo)
            db.session.commit()
            return redirect('/home')
        abort(404)

@app.route("/desc",methods=['GET','POST'])
def desc():
    if current_user.is_authenticated:
        todosComplete  = ToDO.query.filter_by(userId = current_user.id,complete = True).order_by(ToDO.dueDate.desc()).all()
        todosIncomplete  = ToDO.query.filter_by(userId = current_user.id,complete = False).order_by(ToDO.dueDate.desc()).all()
        return render_template("home.html",
        name = current_user.username,
        complete=todosComplete,incomplete = todosIncomplete,userId = current_user.id)
    else:
        return redirect(url_for('login'))

@app.route("/asc",methods=['GET','POST'])
def asc():
    if current_user.is_authenticated:
        todosComplete  = ToDO.query.filter_by(userId = current_user.id,complete = True).order_by(ToDO.dueDate).all()
        todosIncomplete  = ToDO.query.filter_by(userId = current_user.id,complete = False).order_by(ToDO.dueDate).all()
        return render_template("home.html",
        name = current_user.username,
        complete=todosComplete,incomplete = todosIncomplete,userId = current_user.id)
    else:
        return redirect(url_for('login'))
if __name__ == "__main__":
    app.run(port=3000)
 