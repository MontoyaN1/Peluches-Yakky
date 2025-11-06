from website import db
from datetime import datetime


class PqrdStatusHistory(db.Model):
    id_historial = db.Column(db.Integer, primary_key=True)
    id_pqrd = db.Column(db.Integer, db.ForeignKey("pqrd.id_pqrd"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=True)
    estado_anterior = db.Column(db.String(50))
    estado_nuevo = db.Column(db.String(50))
    prioridad_anterior = db.Column(db.String(50))
    prioridad_nueva = db.Column(db.String(50))
    comentario = db.Column(db.Text)
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)
    
    pqrd = db.relationship("Pqrd", backref=db.backref("historial_estados", lazy=True))
