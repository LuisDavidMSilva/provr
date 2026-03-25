from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')


    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        from app.models import user, question, quiz

    from app.blueprints.auth import auth_bp
    from app.blueprints.quiz import quiz_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app