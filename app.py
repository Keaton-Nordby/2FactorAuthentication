from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pyotp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Dummy user database
users = {
    'user': {'password': 'password123', 'secret': pyotp.random_base32()},  # In-memory user data, not secure for production
    'user1': {'password': 'keaton', 'secret': pyotp.random_base32()}
}


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Load user function
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Index route (Landing page with loading)
@app.route('/')
def index():
    return render_template('index.html')

# Login route to handle 2FA
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users.get(username)
        if user and user['password'] == password:
            # Generate OTP for 2FA
            totp = pyotp.TOTP(user['secret'])
            otp = totp.now()  # OTP is generated here
            session['username'] = username
            session['otp'] = otp
            print(f"Generated OTP: {otp}")  # Print OTP in terminal for testing
            return render_template('2fa.html')  # Redirect to OTP verification page
        else:
            return 'Invalid username or password'
    return render_template('login.html')


# 2FA verification route
@app.route('/verify', methods=['POST'])
def verify():
    otp = request.form['otp']
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    user = users.get(username)
    totp = pyotp.TOTP(user['secret'])

    if totp.verify(otp):
        user_obj = User(username)
        login_user(user_obj)
        success_message = f"Welcome {username}! You are successfully logged in."
        return render_template('2fa.html', success_message=success_message)
    else:
        return 'Invalid OTP'

# Dashboard route (protected after successful login)
@app.route('/dashboard')
@login_required
def dashboard():
    print(f"Logged in user: {current_user.id}")  # Print logged-in username for verification
    return f'Welcome {current_user.id}! You are logged in.'

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
