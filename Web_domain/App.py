from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import os
import re
from werkzeug.utils import secure_filename
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = '/static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    

@app.route('/') #This is boots the home page
def index():
    return render_template('index.html')

# --------------------------login page--------------------------


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
            session['username'] = results[0][1]  # Assuming username is the first column
            session['profilepic'] = results[0][5]  # Assuming profilepic is the sixth column
            update_query = 'UPDATE users SET logged_in = 1 WHERE email = %s'
            cursor.execute(update_query, (email,))
            cnx.commit()
            return redirect('/account')
        else:
            return redirect('/signup')
    
    return render_template('login.html')

# ------------------------tools post page ----------------------------

@app.route('/tools', methods=['GET', 'POST'])
def tools():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        print(request.form)  # Debugging statement
        if not all(key in request.form for key in ('title', 'category', 'company', 'content')):
            return "Missing form fields", 400
        
        title = request.form['title']
        category = request.form['category']
        company = request.form['company']
        content = request.form['content']
        profilepic = session.get('profilepic', None)

        try:
            with get_db_connection() as connection:
                cursor = connection.cursor()
                
                insert_post_query = 'INSERT INTO posts (content, username, title, company, category, image_path) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(insert_post_query, (content, session['username'], title, company, category, profilepic))
                post_id = cursor.lastrowid #creates id for each post

                connection.commit()
        except mysql.connector.Error as err:
            print(f"Post failed: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return redirect(url_for('tools'))

    posts = []
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM posts WHERE username = %s', (session['username'],))
            posts = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Fetching posts failed: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return render_template('tools.html', posts=posts)

# ------------------------------------signup---------------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print(request.form)  # Debugging statement
        if not all(key in request.form for key in ('username', 'password', 'email', 'phone', 'interests')):
            return "Missing form fields", 400
        
        try:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            phone = request.form['phone']
            interests = request.form['interests']
            image = request.files['image'] if 'image' in request.files else None
            profilepic = None 

            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                profilepic = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(profilepic)
                profilepic = os.path.join('static/uploads', filename).replace('\\', '/')

            with get_db_connection() as connection:
                cursor = connection.cursor()
                
                # Check if the email is already taken
                check_query = 'SELECT * FROM users WHERE email = %s'
                cursor.execute(check_query, (email,))
                if cursor.fetchone():
                    return "Email is already taken", 69
                check_query = 'SELECT * FROM users WHERE username = %s'
                cursor.execute(check_query, (username,))
                if cursor.fetchone():
                    return "Username is already taken", 69
                
                query = 'INSERT INTO users (username, password, email, phone, interests, profilepic) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(query, (username, password, email, phone, interests, profilepic))
                connection.commit()

            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error: {e}")  # Print the error message
            return "An error occurred", 500

    return render_template('signup.html')
    
    return render_template('signup.html')

# -----------------------account page----------------------

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
    username = session.get('username')
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

# -------------------add tool------------------

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

# ------------------------------Delete Account---------------------------

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']  # Get the logged-in user's username

    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()

            # Call the stored procedure to delete the user and related rows
            cursor.callproc('prc_delete_user', (username,))
            
            # Consume any unread results
            for result in cursor.stored_results():
                result.fetchall()

            connection.commit()

        # Log the user out by clearing the session
        session.pop('username', None)

    except Exception as e:
        print(f"Error deleting profile: {e}")
        return redirect(url_for('account'))  # Redirect to profile in case of error

    # Redirect to the home page after successful deletion
    return redirect(url_for('index'))

# -----------------------------Bookmarks-------------------------

@app.route('/bookmark_post/<int:post_id>', methods=['POST'])
def bookmark_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']  # Get the logged-in user's username

    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()

            # Check if the post is already bookmarked
            cursor.execute("SELECT * FROM bookmarks WHERE username = %s AND post_id = %s", (username, post_id))
            bookmark = cursor.fetchone()

            if bookmark:  # If the post is already bookmarked, remove it
                delete_query = "DELETE FROM bookmarks WHERE username = %s AND post_id = %s"
                cursor.execute(delete_query, (username, post_id))
            else:  # If it's not bookmarked, add it
                insert_query = "INSERT INTO bookmarks (username, post_id) VALUES (%s, %s)"
                cursor.execute(insert_query, (username, post_id))

            connection.commit()
    except Exception as e:
        print(f"Error bookmarking post: {e}")
    return redirect(url_for('account'))



@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'username' not in session:
        return redirect(url_for('index'))

    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()

            # First, delete related entries in the post_hashtags table
            cursor.execute("DELETE FROM post_hashtags WHERE post_id = %s", (post_id,))
            connection.commit()

            # Optionally, delete related bookmarks (if any)
            cursor.execute("DELETE FROM bookmarks WHERE post_id = %s", (post_id,))
            connection.commit()

            # Finally, delete the post
            query = "DELETE FROM posts WHERE id = %s AND username = %s"
            cursor.execute(query, (post_id, session['username']))
            connection.commit()

    except Exception as e:
        print(f"Error deleting post: {e}")
    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)