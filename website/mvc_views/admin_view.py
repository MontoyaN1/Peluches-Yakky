from flask import render_template, Blueprint, request, flash
from flask_login import current_user
from website.controllers.admin_cotller import (
    crer_empleado,
    tasa_conversion,
    promedio_cliente,
    tiempo_respuesta_actividades,
    metricas_retencion_simplificada,
    ciclo_ventas_promedio,
    total_contactos,
    total_oportunidades,
)
from website.decorators import login_required, rol_required
from datetime import datetime, timedelta

mvc_admin = Blueprint("mvc_admin", __name__)


@mvc_admin.route("/crear-empleado", methods=["GET", "POST"])
@login_required
@rol_required(1)
def crear_empleado():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        clave = request.form.get("clave")

        crer_empleado(nombre=nombre, correo=email, clave=clave)

        flash("Empleado creado correctamente")

        return render_template("admin.html")

    return render_template("crear_empleado.html")


@mvc_admin.route("/metricas-crm", methods=["GET", "POST"])
@login_required
@rol_required(1)
def metricas_crm():
    fecha_inicio = (datetime.now() - timedelta(days=30)).replace(
        hour=00, minute=00, second=00, microsecond=00
    )
    fecha_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=00)
    if request.method == "POST":
        fecha_inicio_str = request.form.get("fecha_inicio")
        fecha_fin_str = request.form.get("fecha_fin")

        if fecha_inicio_str and fecha_fin_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
                fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
                fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
                print(f"FORM Inicio: {fecha_inicio}, fin: {fecha_fin}")

            except ValueError:
                flash("Formato de fecha incorrecto", "error")
    else:
        print(f"Inicio: {fecha_inicio}, fin: {fecha_fin}")

    tasa_conversion_dato = tasa_conversion(
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
    )
    promedio_cliente_dato = promedio_cliente(
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
    )
    tiempo_respuesta = tiempo_respuesta_actividades(
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
    )
    tasa_chunk = metricas_retencion_simplificada(
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
    )
    tasa_retencion = tasa_chunk[0]
    churn_rate = tasa_chunk[1]

    ciclo_ventas = ciclo_ventas_promedio(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

    total_contactos_dato = total_contactos(
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
    )

    total_oportunidades_dato = total_oportunidades(
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
    )

    datos_graficos = {
        'metricas_principales': {
            'tasa_conversion': tasa_conversion_dato,
            'promedio_cliente': promedio_cliente_dato,
            'ciclo_ventas': ciclo_ventas,
            'total_contactos': total_contactos_dato,
            'total_oportunidades': total_oportunidades_dato
        },
        'retencion_churn': {
            'tasa_retencion': tasa_retencion,
            'churn_rate': churn_rate
        },
        'tiempo_respuesta': tiempo_respuesta
    }

    return render_template(
        "crm.html",
        fecha_fin=fecha_fin,
        fecha_inicio=fecha_inicio,
        tasa_conversion=tasa_conversion_dato,
        promedio_cliente=promedio_cliente_dato,
        tiempo_respuesta=tiempo_respuesta,
        tasa_retencion=tasa_retencion,
        churn_rate=churn_rate,
        ciclo_ventas=ciclo_ventas,
        total_contactos=total_contactos_dato,
        total_oportunidades=total_oportunidades_dato,
        datos_graficos=datos_graficos
    )
