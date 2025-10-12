from website import db
from website.models.producto_model import Product
from website.models.order_model import Order
from sqlalchemy import func
from website.models.contacto_model import Contacto


def peluches_vendidos_total():
    """Total de peluches vendidos - CORREGIDA"""
    total_peluches = (
        db.session.query(func.sum(Order.quantity))
        .filter(Order.status == "Entregado")
        .scalar()
    )  # ← Asegúrate de usar .scalar()

    return total_peluches or 0


def metricas_experiencia_cliente():
    """Métricas que realmente importan para peluches"""
    total_contactos = Contacto.query.count()

    # 1. CLIENTES FELICES
    clientes_felices = (
        db.session.query(Contacto.id_contacto)
        .filter(
            (Contacto.satisfaccion == 5)
            | (
                Contacto.id_contacto.in_(
                    db.session.query(Order.customer_link)
                    .group_by(Order.customer_link)
                    .having(func.count(Order.id) > 1)
                    .subquery()
                )
            )
        )
        .distinct()
        .count()  # ← .count() retorna un número
    )

    # 2. CLIENTES SATISFECHOS
    clientes_satisfechos = Contacto.query.filter(Contacto.satisfaccion >= 3).count()

    return {
        "clientes_felices": round((clientes_felices / total_contactos) * 100)
        if total_contactos > 0
        else 0,
        "clientes_satisfechos": round((clientes_satisfechos / total_contactos) * 100)
        if total_contactos > 0
        else 0,
    }


def total_ventas_por_producto():
    """Total vendido por cada producto - CORREGIDA"""
    ventas = (
        db.session.query(
            Product.id,
            Product.product_name,
            func.sum(Order.quantity).label("total_vendido"),
        )
        .join(Order, Order.product_link == Product.id)
        .filter(Order.status == "Entregado")
        .group_by(Product.id)
        .order_by(func.sum(Order.quantity).desc())
        .all()  # ← .all() retorna una lista de tuples
    )

    resultado = []
    for producto in ventas:
        resultado.append(
            {
                "id": producto.id,
                "nombre": producto.product_name,
                "total_vendido": producto.total_vendido or 0,
            }
        )

    return resultado


def ventas_mensuales_para_grafica(anio=None):
    """Ventas mensuales formateadas para Chart.js - CORREGIDA"""
    from datetime import datetime

    if not anio:
        anio = datetime.now().year

    ventas_mensuales = (
        db.session.query(
            func.strftime("%m", Order.fecha_creacion).label("mes_num"),
            func.sum(Order.quantity).label("total_vendido"),
        )
        .filter(
            Order.status == "Entregado",
            func.strftime("%Y", Order.fecha_creacion) == str(anio),
        )
        .group_by("mes_num")
        .order_by("mes_num")
        .all()  # ← .all() retorna lista
    )

    meses_es = [
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic",
    ]

    datos_completos = {mes: 0 for mes in meses_es}

    for venta in ventas_mensuales:
        mes_num = int(venta.mes_num)
        if 1 <= mes_num <= 12:
            datos_completos[meses_es[mes_num - 1]] = venta.total_vendido or 0

    return {
        "labels": list(datos_completos.keys()),
        "datos": list(datos_completos.values()),
        "total_anual": sum(datos_completos.values()),
    }  # ← Retorna diccionario simple
