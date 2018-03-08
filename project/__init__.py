import os

from flask import Flask, render_template
#from flask.ext.login import LoginManager
from flask_login import LoginManager
#from flask.ext.bcrypt import Bcrypt
from flask_bcrypt import Bcrypt
from flask_mail import Mail
#from flask.ext.debugtoolbar import DebugToolbarExtension
from flask_debugtoolbar import DebugToolbarExtension
#from flask.ext.sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
toolbar = DebugToolbarExtension(app)
db = SQLAlchemy(app)

from project.main.views import main_blueprint
from project.user.views import user_blueprint

app.register_blueprint(main_blueprint)
app.register_blueprint(user_blueprint)

from project.models import User

login_manager.login_view = "user.login"
login_manager.login_message_category = "danger"


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500