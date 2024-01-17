from flask import Flask, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_login import current_user
from flask_babel import Babel
from web432.models import Users
from web432.database import db
import os
import secrets

login_manager = LoginManager()
migrate = Migrate()
babel = Babel()


def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'instance', '432hz.db')
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['BABEL_DEFAULT_LOCALE'] = 'pt'
    app.config['LANGUAGES'] = ['en', 'pt']
    app.config['UPLOAD_DIRECTORY'] = 'web432/static/images/'
    app.config['LOAD_DIRECTORY'] = 'static/images/'

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    # Register your routes
    from web432.views import register_routes, role_required
    register_routes(app, role_required)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    # Custom Error Pages

    # Invalid URL
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    # Invalid URL
    @app.errorhandler(500)
    def page_not_found(e):
        return render_template('500.html'), 500

    return app

def get_locale():
    return session.get('lang', 'pt')
