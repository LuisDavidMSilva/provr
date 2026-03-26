from flask import render_template
from flask_login import login_required
from . import quiz_bp

@quiz_bp.route('/')
@login_required
def index():
    return render_template('quiz/index.html')