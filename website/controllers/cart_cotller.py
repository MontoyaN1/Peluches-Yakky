from website.models.cart_model import Cart
from sqlalchemy import desc
from website.models.pqrd_model import Pqrd

def buscar_cart(customer_id):
    carrito = Cart.query.filter_by(customer_link=customer_id).all()

    return carrito
