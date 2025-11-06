from flask import Blueprint, render_template, request, redirect, flash
from website.controllers.all_user_cotller import (
    peluches_vendidos_total,
    metricas_experiencia_cliente,
    total_ventas_por_producto,
    ventas_mensuales_para_grafica,
)
from flask_login import current_user

from website.controllers.pqrd_corller import crear_pqrd


todos = Blueprint("todos", __name__)


@todos.route("/sobre-nosotros", methods=["GET", "POST"])
def sobre_nosotros():
    total_peluches = peluches_vendidos_total()

    metricas_clientes = metricas_experiencia_cliente()

    clientes_felices = metricas_clientes["clientes_felices"]  # ← Esto ahora funciona
    clientes_satisfechos = metricas_clientes["clientes_satisfechos"]

    ventas_por_producto = total_ventas_por_producto()

    productos_labels = [p["nombre"] for p in ventas_por_producto[:5]]
    productos_datos = [p["total_vendido"] for p in ventas_por_producto[:5]]

    ventas_mensuales = ventas_mensuales_para_grafica()

    return render_template(
        "sobre-nosotros.html",
        total_peluches=total_peluches,
        clientes_felices=clientes_felices,
        clientes_satisfechos=clientes_satisfechos,
        productos_labels=productos_labels,
        productos_datos=productos_datos,
        ventas_mensuales=ventas_mensuales,
    )


@todos.route("/contacto",methods=["GET", "POST"])
def pqrd():
    if request.method == "POST":
        id_cliente = current_user.id
        nombre = current_user.username
        email = current_user.email
        telefono = current_user.telefono

        tipo_solicitud = request.form.get("tipo_solicitud")
        asunto = request.form.get("asunto")
        descripcion = request.form.get("descripcion")

        try:
            pqrd_creado = crear_pqrd(
                id_cliente=id_cliente,
                nombre=nombre,
                email=email,
                telefono=telefono,
                tipo_solicitud=tipo_solicitud,
                asunto=asunto,
                descripcion=descripcion,
            )
            if pqrd_creado:
                flash("PQRD creado exitosamente")
                return redirect("/")
        except Exception as e:
            flash(e)
            print(e)
            return redirect("/")

    return render_template("contacto.html")


