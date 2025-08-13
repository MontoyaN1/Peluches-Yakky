from flask import Blueprint

auth = Blueprint("auth", __name__)


@auth.route('/')
def home():
    return 'Página de auth'


@auth.route("/login")
def login():
    return "Página de login"


@auth.route("/sing-up")
def sing_up():
    return "Página de iniciar sesión"
