from flask import Blueprint, render_template
from .forms import LoginForm, SingUpForm

auth = Blueprint("auth", __name__)


@auth.route("/sing-up")
def sing_up():
    form = SingUpForm()
    return render_template("nuevo.html")


@auth.route("/login")
def login():
    form = LoginForm()
    return render_template("ingresar.html", form=form)
