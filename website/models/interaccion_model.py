from website import db
from datetime import datetime


class Interaccion(db.Model):
    __tablename__ = "interacciones"

    id_interaccion = db.Column(db.Integer, primary_key=True)

    id_contacto = db.Column(
        db.Integer, db.ForeignKey("contactos.id_contacto"), nullable=False
    )
    id_oportunidad = db.Column(
        db.Integer, db.ForeignKey("oportunidades.id_oportunidad"), nullable=True
    )
    id_agente = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    id_actividad = db.Column(
        db.Integer, db.ForeignKey("actividades.id_actividad"), nullable=True
    )

    tipo_interaccion = db.Column(db.String(50), nullable=False)

    descripcion = db.Column(db.Text, nullable=False)

    resultado = db.Column(db.String(100))

    fecha_interaccion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Interaccion {self.tipo_interaccion} - {self.fecha_interaccion}>"
