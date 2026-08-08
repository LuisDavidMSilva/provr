from flask import render_template, redirect, url_for, flash
from app import db, bcrypt
from app.models.user import User
from app.models.moderation import ContentFilterConfig, ModerationLog
from app.blueprints.auth.forms import RegistrationForm, LoginForm, ChangePasswordForm, UpdateProfilePictureForm, SetNewPassword, RecoveryPassword, GenerateRecoveryKeyForm, ResetPasswordRequestForm
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
import os
import secrets
from PIL import Image


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('quiz.index'))  
    form = RegistrationForm()
    if form.validate_on_submit():
        if db.session.scalar(db.select(User).filter_by(email=form.email.data)):
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('auth.login'))
            
        if db.session.scalar(db.select(User).filter_by(username=form.username.data)):
            flash('Username already taken. Please choose another.', 'danger')
            return redirect(url_for('auth.register'))
        
        recovery_key = '-'.join([secrets.token_hex(4).upper() for _ in range(3)])
        hashed_recovery_key = bcrypt.generate_password_hash(recovery_key).decode('utf-8')

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            recovery_key_hash=hashed_recovery_key
        )
        db.session.add(user)
        db.session.commit()
        return render_template('auth/register_success.html', recovery_key=recovery_key)
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('quiz.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(email=form.email.data))
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

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(email=form.email.data))
        if user and user.username == form.username.data:
            clean_key = form.recovery_key.data.strip().upper()
            if user.recovery_key_hash and bcrypt.check_password_hash(user.recovery_key_hash, clean_key):
                login_user(user)
                flash('Access granted using recovery key. Please change your password.', 'info')
                return redirect(url_for('auth.change_password'))
        flash('Invalid email, username, or recovery key.', 'danger')
    return render_template('auth/reset_password_request.html', form=form)




@auth_bp.route('/update-picture', methods=['GET', 'POST'])
@login_required
def update_picture():
    form = UpdateProfilePictureForm()
    if form.validate_on_submit():
        file = form.picture.data
        
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        # 1. Size Filter Check
        size_cfg = db.session.scalar(db.select(ContentFilterConfig).filter_by(name='max_file_size'))
        if size_cfg and size_cfg.is_active:
            try:
                max_size_mb = float(size_cfg.value)
            except ValueError:
                max_size_mb = 3.0
            if size > max_size_mb * 1024 * 1024:
                reason = f"Upload blocked: profile picture size ({size / (1024*1024):.2f}MB) exceeds limit of {max_size_mb}MB."
                log = ModerationLog(
                    user_id=current_user.id,
                    username=current_user.username,
                    action='blocked',
                    content_type='profile_picture',
                    reason=reason,
                    filename=file.filename
                )
                db.session.add(log)
                db.session.commit()
                flash(reason, 'danger')
                return redirect(url_for('auth.update_picture'))

        # 2. Extension Filter Check
        ext_cfg = db.session.scalar(db.select(ContentFilterConfig).filter_by(name='blocked_extensions'))
        if ext_cfg and ext_cfg.is_active:
            ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            blocked_exts = [e.strip().lower() for e in ext_cfg.value.split(',') if e.strip()]
            if ext in blocked_exts:
                reason = f"Upload blocked: file extension '.{ext}' is prohibited."
                log = ModerationLog(
                    user_id=current_user.id,
                    username=current_user.username,
                    action='blocked',
                    content_type='profile_picture',
                    reason=reason,
                    filename=file.filename
                )
                db.session.add(log)
                db.session.commit()
                flash(reason, 'danger')
                return redirect(url_for('auth.update_picture'))
            
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


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('quiz.index'))
    form = RecoveryPassword()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(email=form.email.data))
        if user:
            if not user.recovery_key_hash:
                flash('This account does not have a recovery key configured.', 'danger')
                return redirect(url_for('auth.reset_password'))

            clean_key = form.recovery_key.data.strip().upper()
            if bcrypt.check_password_hash(user.recovery_key_hash, clean_key):
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user.password_hash = hashed_password
                db.session.commit()
                flash('Password reset successfully! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
        
        flash('Invalid email or recovery key.', 'danger')
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/recovery-key', methods=['GET', 'POST'])
@login_required
def recovery_key():
    form = GenerateRecoveryKeyForm()
    new_key = None
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password_hash, form.password.data):
            new_key = '-'.join([secrets.token_hex(4).upper() for _ in range(3)])
            hashed_recovery_key = bcrypt.generate_password_hash(new_key).decode('utf-8')
            current_user.recovery_key_hash = hashed_recovery_key
            db.session.commit()
            flash('New recovery key generated successfully!', 'success')
        else:
            flash('Incorrect password.', 'danger')
    return render_template('auth/recovery_key.html', form=form, new_key=new_key)