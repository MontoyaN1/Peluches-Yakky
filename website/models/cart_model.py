from website import db


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    # customer product

    def __str__(self):
        return "<Cart %r>" % self.id