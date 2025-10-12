from website import db


import uuid
from datetime import datetime


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), default="Pendiente")
    payment_id = db.Column(db.String(1000), default=lambda: str(uuid.uuid4())[:8])
    address = db.Column(db.String(1000), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    forma_pago = db.Column(db.String(20), nullable=False)
    fecha_creacion = db.Column(db.DateTime(), default=datetime.utcnow)

    customer_link = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    # customer

    def __str__(self):
        return "<Order %r>" % self.id