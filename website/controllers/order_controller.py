import pandas as pd
from website.models.order_model import Order


def buscar_order(customer_id):
    pedidos = Order.query.filter_by(customer_link=customer_id).all()

    return pedidos


def obtener_ventas_producto(producto_id):
    """Obtiene el historial de ventas de un producto"""
    try:
        # Asumiendo que tienes un modelo Venta
        ventas = Order.query.filter_by(product_link=producto_id).all()

        if not ventas:
            return pd.DataFrame(columns=["fecha", "cantidad"])

        historial_ventas = pd.DataFrame(
            [
                {
                    "fecha": venta.fecha_creacion,
                    "cantidad": venta.quantity,
                }
                for venta in ventas
            ]
        )

        return historial_ventas

    except Exception as e:
        print(f"❌ Error obteniendo ventas del producto {producto_id}: {e}")
        return pd.DataFrame(columns=["fecha", "cantidad"])


def obtener_historial_cliente(cliente_id):
    """Obtiene el historial de compras de un cliente"""
    try:
        compras = Order.query.filter_by(customer_link=cliente_id).all()

        if not compras:
            return pd.DataFrame(columns=["fecha", "monto"])

        historial_compras = pd.DataFrame(
            [
                {
                    "fecha": compra.fecha_creacion,
                    "monto": compra.price
                    if hasattr(compra, "price")
                    else 1,  # Si no hay monto, contar como 1
                }
                for compra in compras
            ]
        )

        return historial_compras

    except Exception as e:
        print(f"❌ Error obteniendo historial del cliente {cliente_id}: {e}")
        return pd.DataFrame(columns=["fecha", "monto"])
