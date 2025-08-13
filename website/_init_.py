from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "abcde"

    from .views import views
    from .admin import admin
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(admin, url_prefix="/")

    return app
