from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.sqlite3"


def create_database():
    db.create_all()
    print("Base de Datos creada")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "8=F&9w4Z{F"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

    db.init_app(app)

    @app.errorhandler(404)
    def error_404(error):
        return render_template("error_404.html")

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .views import views
    from .admin import admin
    from .auth import auth
    from .models import Customer, Cart, Product, Order  # noqa: F401
    from sqlalchemy_utils import database_exists

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))

    def create_admin():
        admin = Customer()
        admin.username = "Admin"
        admin.email = "admin@peluchesyakky.com"
        admin.password = "TSzxvDl1nQ"

        try:
            db.session.add(admin)
            db.session.commit()
            print("Admin creado")

        except Exception as e:
            db.session.rollback()
            print(f"Fallo crear admin  {e}")

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(admin, url_prefix="/")

    with app.app_context():
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            db.create_all()
            print("Base de Datos creada")

            # Crear admin solo si no existe
            if not Customer.query.filter_by(email="admin@peluchesyakky.com").first():
                create_admin()
        else:
            print("La base de datos ya existe, omitiendo creación")

    return app
