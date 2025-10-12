from website import db
from datetime import datetime


class Oportunidad(db.Model):
    __tablename__ = "oportunidades"

    id_oportunidad = db.Column(db.Integer, primary_key=True)

    id_contacto = db.Column(
        db.Integer, db.ForeignKey("contactos.id_contacto"), nullable=False
    )
    id_cliente = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=True)
    id_agente = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)

    titulo = db.Column(db.String(150), nullable=False)
    valor_estimado = db.Column(db.DECIMAL(10, 2))
    etapa = db.Column(db.String(50), default="nueva")
    probabilidad = db.Column(db.Integer, default=0)
    descripcion = db.Column(db.Text)

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_cierre = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Oportunidad {self.titulo} - {self.etapa}>"
