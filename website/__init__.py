from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager




db = SQLAlchemy()
DB_NAME = "database.sqlite3"
ADMIN_NAME = "Admin"
ADMIN_EMAIL = "admin@peluchesyakky.com"
ADMIN_PASS = "TSzxvDl1nQ"


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
    from .mvc_views.auth_view import auth
    from website.mvc_views.employee_view import employee
    from website.mvc_views.admin_view import mvc_admin
    from website.mvc_views.all_user_view import todos

    from .models.order_model import Order  # noqa: F401

    from website.models.contacto_model import Contacto
    from website.models.oportunidad_model import Oportunidad
    from website.models.actividad_model import Actividad  
    from website.models.interaccion_model import Interaccion
    from sqlalchemy_utils import database_exists
    from .decorators import login_required, rol_required, roles_required

    @login_manager.user_loader
    def load_user(id):
        from website.models.customer_model import Customer
        return Customer.query.get(int(id))

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(admin, url_prefix="/")
    app.register_blueprint(employee, url_prefix="/empleado")
    app.register_blueprint(mvc_admin, url_prefix="/admin")
    app.register_blueprint(todos, url_prefix="/")



    with app.app_context():
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            create_database()
            create_initial_roles()
            create_admin()

        else:
            print("La base de datos ya existe, omitiendo creación")

    return app
__all__ = ['login_required', 'rol_required', 'roles_required', 'db', 'login_manager']


def create_database():
    db.create_all()
    print("Base de Datos creada")

def create_initial_roles():
    """Crear roles con autoflush deshabilitado"""
    try:
        from website.models.rol_model import Rol
        
        roles = ["administrador", "empleado", "cliente"]
        
        # Deshabilitar autoflush temporalmente
        with db.session.no_autoflush:
            for rol_nombre in roles:
                if not Rol.query.filter_by(nombre_rol=rol_nombre).first():
                    rol = Rol(nombre_rol=rol_nombre)
                    db.session.add(rol)
            
            # Commit manual una vez
            db.session.commit()
            print("✓ Roles iniciales creados")
            
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creando roles: {e}")

def create_admin():
    """Crear admin después de los roles"""
    try:
        from website.models.customer_model import Customer
        
        # Verificar si ya existe
        if Customer.query.filter_by(email=ADMIN_EMAIL).first():
            print("✓ Admin ya existe")
            return
            
        admin = Customer(
            username=ADMIN_NAME,
            email=ADMIN_EMAIL, 
            password=ADMIN_PASS,
            rol_id=1  
        )
        
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin creado exitosamente")
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creando admin: {e}")