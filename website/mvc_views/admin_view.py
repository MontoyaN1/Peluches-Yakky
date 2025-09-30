from flask import render_template, Blueprint, request, flash
from flask_login import current_user
from website.controllers.admin_cotller import crer_empleado

mvc_admin = Blueprint("mvc_admin", __name__)


@mvc_admin.route("/crear-empleado", methods=["GET", "POST"])
def crear_empleado():
    if current_user.rol_id == 1:
        if request.method == "POST":
            nombre = request.form.get("nombre")
            email = request.form.get("email")
            clave = request.form.get("clave")

            crer_empleado(nombre=nombre, correo=email, clave=clave)

            flash("Empleado creado correctamente")

            return render_template("admin.html")

        return render_template("crear_empleado.html")
    return render_template("home.html")
