from flask import render_template, redirect, url_for, flash
from . import auth_bp

@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')

@auth_bp.route('/register')
def register():
    return render_template('auth/register.html')