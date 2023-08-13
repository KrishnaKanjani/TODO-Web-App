from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Internship/Python-Practice/Day10/TODO APP/todo.db'
db = SQLAlchemy(app=app)
app.secret_key = 'mykey'

# TO-DO CLASS
class TODO(db.Model):
    id = db.Column('task_id', db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __init__(self, task, done, user_id):
        self.task = task
        self.done = done
        self.user_id = user_id

# USER CLASS (for user registration)
class USER(db.Model):
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    c_password = db.Column(db.String(80), nullable=False)
    todos = db.relationship('TODO', backref='user', lazy=True)

    def __init__(self, username, password, c_password):
        self.username = username
        self.password = password
        self.c_password = c_password

# INITIAL ROUTE
@app.route('/')
def index():    
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        username = session.get('username')
        user = USER.query.filter_by(username=username).first()
        todos = TODO.query.filter_by(user_id=user.id).all()    
    return render_template('index.html', todos=todos, username=username, user=user)

# ROUTE FOR USER REGISTRATION
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['c_password']

        if password != confirm_password:
            # Password do not match
            flash('Passwords do not match. Please try again.')
            return render_template('register.html', message='Passwords do not match. Please try again.')

        if USER.query.filter_by(username=username).first():
            # Password already taken
            flash('Username already taken. Please choose a different one.')
            return render_template('register.html', message='Username already taken. Please choose a different one.')
        else:
            new_user = USER(username=username, password=password, c_password=confirm_password)
            db.session.add(new_user)
            db.session.commit()
            # Store the username in the session
            session['username'] = username  
            return redirect(url_for('index'))
    return render_template('register.html')

# ROUTE FOR USER LOGIN
@app.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = USER.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            print('Login successful.')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.')
            return render_template('login.html', message='Invalid credentials. Please try again.')
    return render_template('login.html')

# ROUTE FOR ADDING NEW TO-DO
@app.route('/add', methods = ['GET', 'POST'])
def add():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        username = session['username']
        user = USER.query.filter_by(username=username).first()
        newTodo = request.form['newTodo']
        add_todo = TODO(task=newTodo, user_id=user.id, done=False) 
        db.session.add(add_todo)
        db.session.commit()
        return redirect(url_for('index'))

# ROUTE FOR DELETING THE TO-DO
@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    todo_to_be_deleted = TODO.query.get(todo_id)

    if todo_to_be_deleted:
        db.session.delete(todo_to_be_deleted)
        db.session.commit()
        return redirect(url_for('index'))

# ROUTE TO UPDATE A TO-DO
@app.route('/update/<int:todo_id>', methods=['GET', 'POST'])
def update(todo_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    todo_to_update = TODO.query.get(todo_id)

    if request.method == 'GET':
        try:
            new_task = request.args.get('task_name')
            if new_task:
                todo_to_update.task = new_task
                db.session.commit()
        except Exception as e:
            print("Error:", e)
    return redirect(url_for('index'))

# ROUTE TO UPDATE THE CHECKBOX
@app.route('/checked/<int:todo_id>', methods=['GET'])
def update_done(todo_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    todo_to_update = TODO.query.get(todo_id)

    done = request.args.get('done')
    if done == 'true':
        todo_to_update.done = True
    elif done == 'false':
        todo_to_update.done = False

    db.session.commit()
    return redirect(url_for('index'))

# ROUTE FOR USER LOGOUT
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    print('Logout Successfull')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
