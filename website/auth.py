from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Customer
from ._init_ import db
from flask_login import login_user, logout_user, login_required

auth = Blueprint("auth", __name__)


@auth.route("/sing-up", methods=["GET", "POST"])
def sing_up():

    if request.method == "POST":
        username = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("clave")

        new_customer = Customer()
        new_customer.username = username
        new_customer.email = email
        new_customer.password = password

        try:
            db.session.add(new_customer)
            db.session.commit()
            flash("Cuenta creada exitosamente, Puedes inicar sesión")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Fallo creación de cuenta: {e}")

    return render_template("nuevo.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("clave")

        customer = Customer.query.filter_by(email=email).first()

        if customer:
            if customer.verify_password(password=password):
                flash("Bienvenido")
                login_user(customer)
                return redirect("/")
            else:
                flash("Contraseña incorrecta")

        else:
            flash("El usaurio no existe, crea una cuenta")

    return render_template("ingresar.html")


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def log_out():
    logout_user()
    return redirect("/")


@auth.route("/profile/<int:customer_id>")
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    print("Customer ID:", customer_id)
    return render_template("profile.html", customer=customer)
