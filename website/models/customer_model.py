from website import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from datetime import datetime


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    rol_id = db.Column(
        db.Integer, db.ForeignKey("rol.id_rol"), nullable=True, default=3
    )
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(150))
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    telefono = db.Column(db.Integer, nullable=True)

    cart_items = db.relationship(
        "Cart", backref=db.backref("customer", lazy=True), cascade="all, delete-orphan"
    )
    orders = db.relationship(
        "Order", backref=db.backref("customer", lazy=True), cascade="all, delete-orphan"
    )

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True  # Para usuarios reales siempre True

    @property
    def is_active(self):
        """Return True if the user is active."""
        return self.active  # Usa el campo que agregaste

    @property
    def is_anonymous(self):
        """Return True if this is an anonymous user."""
        return False  # Para usuarios reales siempre False

    def get_id(self):
        """Return the user ID as string."""
        return str(self.id)

    @property
    def password(self):
        raise AttributeError("Password is not a readable Attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def __str__(self):
        return "<Customer %r>" % Customer.id
