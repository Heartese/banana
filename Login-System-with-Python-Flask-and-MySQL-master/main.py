from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'loginapp')

mysql = MySQL(app)

@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            flash("Incorrect username/password!", "danger")
    return render_template('auth/login.html', title="Login")

@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and all(k in request.form for k in ('username', 'password', 'email')):
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "danger")
        elif not username or not password or not email:
            flash("Please fill out the form completely!", "danger")
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)',
                           (username, hashed_password, email))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for('login'))
    elif request.method == 'POST':
        flash("Please fill out the form!", "danger")
    return render_template('auth/register.html', title="Register")

@app.route('/home')
def home():
   
    if 'loggedin' in session:
        return redirect("http://localhost:4000/")
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('login'))  

@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
