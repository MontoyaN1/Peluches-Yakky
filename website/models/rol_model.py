from website import db


class Rol(db.Model):
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(100), nullable=False)

    usuarios = db.relationship("Customer", backref=db.backref("rol", lazy=True))