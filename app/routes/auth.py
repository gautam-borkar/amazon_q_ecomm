from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.user import User
from app.utils.auth_utils import generate_otp_secret, generate_otp, verify_otp, send_email

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists')
            return redirect(url_for('auth.register'))
        
        # Check if username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        
        # Create new user
        otp_secret = generate_otp_secret()
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='sha256'),
            otp_secret=otp_secret
        )
        
        # Add user to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
        
        # Store user ID in session for OTP verification
        session['user_id'] = user.id
        
        # Generate and send OTP
        otp = generate_otp(user.otp_secret)
        send_email(
            user.email,
            'Your OTP for Login',
            f'Your OTP for login is: {otp}. It will expire in 30 seconds.'
        )
        
        return redirect(url_for('auth.verify_otp'))
    
    return render_template('auth/login.html')

@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        user_id = session['user_id']
        
        user = User.query.get(user_id)
        if not user:
            flash('User not found')
            return redirect(url_for('auth.login'))
        
        if verify_otp(user.otp_secret, otp):
            # OTP is valid, log in the user
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid OTP. Please try again.')
    
    return render_template('auth/verify_otp.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Check if current password is correct
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect')
            return redirect(url_for('auth.change_password'))
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match')
            return redirect(url_for('auth.change_password'))
        
        # Update password
        current_user.password = generate_password_hash(new_password, method='sha256')
        db.session.commit()
        
        flash('Password updated successfully')
        return redirect(url_for('main.profile'))
    
    return render_template('auth/change_password.html')

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate a reset token (in a real app, use a secure token)
            reset_token = generate_password_hash(user.email + str(user.id), method='sha256')[:20]
            
            # Store token in session (in a real app, store in database with expiration)
            session['reset_token'] = reset_token
            session['reset_user_id'] = user.id
            
            # Send reset email
            reset_link = url_for('auth.reset_password', token=reset_token, _external=True)
            send_email(
                user.email,
                'Password Reset Request',
                f'Click the following link to reset your password: {reset_link}'
            )
        
        # Always show success message to prevent email enumeration
        flash('If your email is registered, you will receive a password reset link')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Check if token is valid
    if 'reset_token' not in session or session['reset_token'] != token:
        flash('Invalid or expired reset token')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Check if passwords match
        if new_password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('auth.reset_password', token=token))
        
        # Update user's password
        user_id = session['reset_user_id']
        user = User.query.get(user_id)
        
        if user:
            user.password = generate_password_hash(new_password, method='sha256')
            db.session.commit()
            
            # Clear session data
            session.pop('reset_token', None)
            session.pop('reset_user_id', None)
            
            flash('Password has been reset successfully')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')