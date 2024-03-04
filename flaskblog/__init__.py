from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug import security
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config

bcrypt=security
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flaskblog.users.routes import users
    from flaskblog.professors.routes import professors
    from flaskblog.students.routes import students
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(professors)
    app.register_blueprint(students)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
