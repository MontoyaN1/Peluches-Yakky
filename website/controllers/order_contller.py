



from website.models.order_model import Order


def buscar_order(customer_id):
    pedidos = Order.query.filter_by(customer_link=customer_id).all()

    return pedidos
