from website import db


from datetime import datetime


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)

    current_price = db.Column(db.Integer, nullable=False)

    precio_costo = db.Column(db.Integer, nullable=False)  # tarea
    previous_price = db.Column(db.Integer, nullable=False)

    in_stock = db.Column(db.Integer, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)

    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(1000), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)

    carts = db.relationship(
        "Cart", backref=db.backref("product", lazy=True), cascade="all, delete-orphan"
    )
    orders = db.relationship(
        "Order", backref=db.backref("product", lazy=True), cascade="all, delete-orphan"
    )

    def __str__(self):
        return "<Product %r>" % self.product_name
