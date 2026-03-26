from flask import render_template, redirect, url_for, flash
from app import db, bcrypt
from app.models.user import User
from app.blueprints.auth.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required
from . import auth_bp


@auth_bp.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User (
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created sucessfully! You can now log in', 'sucess')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in sucessfully', 'sucess')
            return redirect(url_for('quiz.index'))
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html', form=form)

@login_required
def index():
    return render_template('quiz/index.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

