from .models import Vote, User
import os
import pymongo
from flask import Flask
from flask_login import (
    LoginManager,
)

MONGODB_CLIENT_URI = os.environ.get('MONGODB_CLIENT_URI', None).replace('"', '')
client = pymongo.MongoClient(MONGODB_CLIENT_URI)
db = client["Glosowanie"]


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(db, user_id)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return app