from flask import Blueprint, render_template
from website.controllers.all_user_cotller import (
    peluches_vendidos_total,
    metricas_experiencia_cliente,
    total_ventas_por_producto,
    ventas_mensuales_para_grafica,
)


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
