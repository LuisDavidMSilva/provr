from flask import render_template, redirect, url_for, flash
from app import db, bcrypt
from app.models.user import User
from app.blueprints.auth.forms import RegistrationForm, LoginForm, ChangePasswordForm, UpdateProfilePictureForm
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
import os
from PIL import Image


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('quiz.index'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password_hash, form.current_password.data):
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password_hash = hashed_password
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('quiz.index'))
        flash('Current password is incorrect.', 'danger')
    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/update-picture', methods=['GET', 'POST'])
@login_required
def update_picture():
    form = UpdateProfilePictureForm()
    if form.validate_on_submit():
        file = form.picture.data
        upload_folder = os.path.join('app', 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        filename = f"user_{current_user.id}.jpg"
        filepath = os.path.join(upload_folder, filename)

        img = Image.open(file)
        img = img.convert('RGB')
        img = img.resize((256, 256))
        img.save(filepath)

        current_user.profile_picture = f"uploads/{filename}"
        db.session.commit()
        flash('Profile picture updated successfully!', 'success')
        return redirect(url_for('quiz.index'))
    return render_template('auth/update_picture.html', form=form)