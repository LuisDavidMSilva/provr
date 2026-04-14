from flask import Flask, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app(config_name='development'):
    app = Flask(__name__)

    config_map = {
        'development': 'config.DevelopmentConfig',
        'production': 'config.ProductionConfig',
        
    }
    app.config.from_object(config_map.get(config_name, 'config.DevelopmentConfig'))

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'danger'
    
    with app.app_context():
        from app.models import user, question, quiz

    from app.blueprints.auth import auth_bp
    from app.blueprints.quiz import quiz_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    @app.route('/terms')
    def terms():
        return render_template('terms.html')

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('500.html'), 500

    return app