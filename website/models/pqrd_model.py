from website import db
from datetime import datetime


class Pqrd(db.Model):
    id_pqrd = db.Column(db.Integer, primary_key=True)
    
    
    id_agente = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)

    
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)  
    tipo_solicitud = db.Column(db.String(50), nullable=False)
    asunto = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False) 
    prioridad = db.Column(db.String(50), nullable=False, default="Media")
    estado = db.Column(db.String(50), nullable=False, default="Abierto")

    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_completada = db.Column(db.DateTime, nullable=True)

    
    agente = db.relationship(
        "Customer", 
        foreign_keys=[id_agente],
        backref=db.backref("pqrds_asignadas", lazy=True)
    )
    
    cliente = db.relationship(
        "Customer", 
        foreign_keys=[id_cliente],
        backref=db.backref("pqrds_creadas", lazy=True)
    )

    def __repr__(self):
        return f'<PQRD {self.id_pqrd} - {self.asunto}>'
