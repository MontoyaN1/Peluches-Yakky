from website import db
from datetime import datetime


class Actividad(db.Model):
    __tablename__ = "actividades"

    id_actividad = db.Column(db.Integer, primary_key=True)

    id_contacto = db.Column(
        db.Integer, db.ForeignKey("contactos.id_contacto"), nullable=False
    )
    id_oportunidad = db.Column(
        db.Integer, db.ForeignKey("oportunidades.id_oportunidad"), nullable=True
    )
    id_agente = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)

    tipo_actividad = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)

    fecha_programada = db.Column(db.DateTime, nullable=False)

    estado = db.Column(db.String(50), default="Pendiente")

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_completada = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Actividad {self.titulo} - {self.estado}>"
