from datetime import datetime, timezone
from flask import Flask, redirect, render_template, url_for, session, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_babel import Babel, gettext as _
from flask_limiter import Limiter, RateLimitExceeded
from flask_limiter.util import get_remote_address


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
babel = Babel()
limiter = Limiter(key_func=get_remote_address)

def get_locale():

    lang = request.args.get('lang')
    if lang in ['en', 'pt_BR', 'es']:
        return lang

    if current_user.is_authenticated:
        try:
            if current_user.locale:
                return current_user.locale
        except Exception:
            pass

    session_lang = session.get('lang')
    if session_lang in ['en', 'pt_BR', 'es']:
        return session_lang

    return request.accept_languages.best_match(['en', 'pt_BR', 'es']) or 'en'

def create_app(config_name='development'):
    app = Flask(__name__)

    config_map = {
        'development': 'config.DevelopmentConfig',
        'production': 'config.ProductionConfig',
        'testing': 'config.TestingConfig'
    }
    app.config.from_object(config_map.get(config_name, 'config.DevelopmentConfig'))

    # Metadata para monitoramento
    app.config['START_TIME'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    app.context_processor(lambda: dict(get_locale=get_locale))
    
    # Inicializar Limiter
    limiter.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'danger'
    
    with app.app_context():
        from app.models import user, question, quiz, moderation

    from app.blueprints.auth import auth_bp
    from app.blueprints.quiz import quiz_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.health import health_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(health_bp, url_prefix='/health')

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

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({
                'error': 'Too many requests',
                'message': str(e.description)
            }), 429
        
        flash(_('Too many requests. Please try again later.'), 'danger')
        return redirect(request.referrer or url_for('auth.login'))

    return app