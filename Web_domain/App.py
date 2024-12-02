from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to get a database connection
def get_db_connection():
    return mysql.connector.connect(
        username='root',
        password='8D452-3GhD56-6Gi!"',
        host='localhost',
        database='userdata'
    )

# Connect to the database
cnx = get_db_connection()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = cnx.cursor()
        query = 'SELECT * FROM users WHERE email = %s AND password = %s'
        cursor.execute(query, (email, password))
        results = cursor.fetchall()

        if results:
            session['email'] = email
            session['username'] = results[0][0]  # Assuming username is the second column
            session['profilepic'] = results[0][5]  # Assuming profilepic is the sixth column
            update_query = 'UPDATE users SET logged_in = 1 WHERE email = %s'
            cursor.execute(update_query, (email,))
            cnx.commit()
            return redirect('/account')
        else:
            return redirect('/signup')
    
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print(request.form)  # Debugging statement
        if not all(key in request.form for key in ('username', 'password', 'email', 'phone', 'interests', 'profilepic')):
            return "Missing form fields", 400
        
        try:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            phone = request.form['phone']
            interests = request.form['interests']
            profilepic = request.form['profilepic']

            with get_db_connection() as connection:
                cursor = connection.cursor()
                
                # Check if the email is already taken
                check_query = 'SELECT * FROM users WHERE email = %s'
                cursor.execute(check_query, (email,))
                if cursor.fetchone():
                    return "Email is already taken", 69
                
                query = 'INSERT INTO users (username, password, email, phone, interests, profilepic) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(query, (username, password, email, phone, interests, profilepic))
                connection.commit()

            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error: {e}")  # Print the error message
            return "An error occurred", 500
    
    return render_template('signup.html')

@app.route('/account')
def account():
    if 'email' in session:
        email = session['email']
        username = session['username']
        profilepic = session['profilepic']
        return render_template('account.html', email=email, username=username, profilepic=profilepic)
    else:
        return redirect(url_for('login'))

@app.route('/loggedin')
def loggedin():
    if 'email' in session:
        email = session['email']
        username = session['username']
        return render_template('loggedin.html', email=email, username=username)
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    if 'username' not in session:
        return redirect(url_for('login'))

        with get_db_connection() as connection:
            cursor = connection.cursor()
            query = 'UPDATE users SET logged_in = 0 WHERE username = %s'
            cursor.execute(query, (username,))
            connection.commit()

        session.pop('email', None)
        print(f"user, {username} has logged out")
    return redirect('/')

# ------------------contact form-------------------

@app.route('/contactform', methods=['GET', 'POST'])
def contactform():
    if request.method == 'POST':
        print(request.form)  # Debugging statement
        if not all(key in request.form for key in ('name', 'email', 'message')):
            return "Missing form fields", 400
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone')  # Use .get() to handle optional fields
        message = request.form['message']

        with get_db_connection() as connection:
            cursor = connection.cursor()
            query = 'INSERT INTO contact (name, email, phone, message) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (name, email, phone, message))
            connection.commit()

        return redirect(url_for('index'))
    return render_template('index.html')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')


@app.route('/addtool', methods=['POST','Get'])
def addtool():
    
    if request.method == 'POST':
       
        name = request.form['name']
        company = request.form['company']
        category = request.form['category']
        description = request.form['description']
        link = request.form['link']

        with get_db_connection() as connection:
            cursor = connection.cursor()
            query = 'INSERT INTO tools (name, company, category, description, link ) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(query, (name, company, category, description, link))
            connection.commit()

        return redirect(url_for('account'))
    
    else: 
        return render_template('addtool.html')


if __name__ == '__main__':
    app.run(debug=True)