from flask import Blueprint, render_template, request, flash, redirect, url_for

from ..models.cart_model import Cart

from ..models.customer_model import Customer
from ..models.order_model import Order
from .. import db
from flask_login import current_user, login_user, logout_user, login_required
from ..controllers.customer_cotller import (
    validar_customer,
    crear_customer,
    buscar_customer,
)
from ..controllers.order_controller import buscar_order
from ..controllers.pqrd_corller import mostrar_pqrd_cliente




auth = Blueprint("auth", __name__)


@auth.route("/sing-up", methods=["GET", "POST"])
def sing_up():
    if request.method == "POST":
        username = request.form.get("nombre")
        email = request.form.get("email")
        telefono = request.form.get("telefono")

        password = request.form.get("clave")

        customer_creado = crear_customer(
            username=username, email=email, password=password, telefono=telefono
        )

        if customer_creado:
            flash(f"Bienvenido {customer_creado.username}")
            return redirect(url_for("auth.login"))

        flash(f"Error al crear cuenta: {customer_creado}")

    return render_template("nuevo.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("clave")

        try:
            usuario = validar_customer(email=email, password=password)
            if usuario:
                login_user(usuario)
                return redirect("/")

        except Exception as e:
            flash(f" {e}")

    return render_template("ingresar.html")


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def log_out():
    logout_user()
    return redirect("/")


@auth.route("/profile")
@login_required
def profile():
    customer_id = current_user.id
    customer = buscar_customer(customer_id=customer_id)
    pedidos = buscar_order(customer_id=customer_id)
    ticktes = mostrar_pqrd_cliente(id_cliente=customer_id)
    print("Customer ID:", customer_id)

    return render_template("profile.html", customer=customer, pedidos=pedidos, ticktes=ticktes)
