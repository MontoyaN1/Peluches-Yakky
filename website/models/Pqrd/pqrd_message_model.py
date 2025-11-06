from website import db
from datetime import datetime


class PqrdMessage(db.Model):
    id_mensaje = db.Column(db.Integer, primary_key=True)
    id_pqrd = db.Column(db.Integer, db.ForeignKey("pqrd.id_pqrd"), nullable=False)
    id_remitente = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    tipo_remitente = db.Column(db.String(20), nullable=False)  # 'cliente', 'agente', 'sistema'
    mensaje = db.Column(db.Text, nullable=False)
    es_automatico = db.Column(db.Boolean, default=False)  # Para mensajes del bot
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    pqrd = db.relationship("Pqrd", backref=db.backref("mensajes", lazy=True))
    remitente = db.relationship("Customer")