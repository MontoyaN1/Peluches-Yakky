from website import db
from datetime import datetime


class Contacto(db.Model):
    __tablename__ = "contactos"

    id_contacto = db.Column(db.Integer, primary_key=True)

    id_agente = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)

    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    empresa = db.Column(db.String(100), nullable=True)

    canal = db.Column(db.String(50))
    estado = db.Column(db.String(50), default="Nuevo")
    satisfaccion = db.Column(db.Integer, nullable=True)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actulizar = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    agente = db.relationship("Customer", backref=db.backref("contactos", lazy=True))
    oportunidades = db.relationship("Oportunidad", backref="contacto", lazy=True)
    actividades = db.relationship("Actividad", backref="contacto", lazy=True)
    interacciones = db.relationship("Interaccion", backref="contacto", lazy=True)

    def __repr__(self):
        return f"<Contacto {self.nombre} - {self.email}>"

    def to_dict(self):
        """Método útil para convertir a JSON"""
        return {
            "id_contacto": self.id_contacto,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "empresa": self.empresa,
            "estado": self.estado,
            "fecha_registro": self.fecha_registro.isoformat(),
        }
