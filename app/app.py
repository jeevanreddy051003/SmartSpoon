from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from recipe_assistant import get_recipe_suggestions, get_recipe_instructions_by_name, get_recipe_instructions_from_image
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'b9f29492e4c9fdea830e39aa284c11e1'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '0511'
app.config['MYSQL_DB'] = 'user_db'

mysql = MySQL(app)

# Define the UPLOAD_FOLDER and ensure it exists
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set the UPLOAD_FOLDER in app configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    # Check if user is not logged in, redirect to login
    if 'username' not in session:
        flash("Please log in to access the page.")
        return redirect(url_for('login'))
    
    # User is logged in, show home page
    return render_template('index.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to home
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate input
        if not username or not password:
            flash("Please enter both username and password.")
            return render_template('login.html')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                # Successful login
                session['username'] = user['username']
                session['user_id'] = user['id']  # Assuming you have an id column
                flash("Login successful!")
                return redirect(url_for('home'))
            else:
                flash("Invalid username or password.")
                return render_template('login.html')
        
        except Exception as e:
            # Log the error (in a real app, use proper logging)
            print(f"Login error: {e}")
            flash("An error occurred. Please try again.")
            return render_template('login.html')
        
        finally:
            cursor.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove user from session
    session.pop('username', None)
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not username or not password or not confirm_password:
            flash("All fields are required.")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('register'))

        # Check password strength (optional but recommended)
        if len(password) < 8:
            flash("Password must be at least 8 characters long.")
            return redirect(url_for('register'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username already exists.")
                return redirect(url_for('register'))

            # Hash the password
            hashed_password = generate_password_hash(password)
            
            # Insert new user
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                           (username, hashed_password))
            mysql.connection.commit()
            
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
        
        except Exception as e:
            # Log the error (in a real app, use proper logging)
            print(f"Registration error: {e}")
            flash("An error occurred during registration.")
            return redirect(url_for('register'))
        
        finally:
            cursor.close()

    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        # Implement password reset logic here (e.g., sending an email with a reset link)
        flash('A password reset link has been sent to your email.')
        return redirect(url_for('login'))

    return render_template('forgot_password.html')

# Rest of your existing routes remain the same
@app.route('/suggest_recipes', methods=['POST'])
def suggest_recipes():
    ingredients = request.form.get('ingredients', '').split(',')
    recipes = get_recipe_suggestions([i.strip() for i in ingredients])

    if isinstance(recipes, str):
        recipes = [recipe.strip() for recipe in recipes.split('\n') if recipe.strip()]

    return jsonify({'recipes': recipes})

@app.route('/get_instructions', methods=['POST'])
def get_instructions():
    recipe_name = request.form.get('recipe_name', '')
    instructions = get_recipe_instructions_by_name(recipe_name)

    return jsonify({'instructions': instructions})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'})

    image = request.files['image']

    if image.filename == '':
        return jsonify({'error': 'No selected file'})

    if not allowed_file(image.filename):
        return jsonify({'error': 'Invalid file type. Only png, jpg, jpeg, and gif are allowed.'})


    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)

    try:
        instructions = get_recipe_instructions_from_image(filename)
        return jsonify({'instructions': instructions})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/results', methods=['GET'])
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)