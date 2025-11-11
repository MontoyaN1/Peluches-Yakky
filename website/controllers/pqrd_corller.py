from website import db
from ..models.pqrd.pqrd_message_model import PqrdMessage
from ..models.pqrd.pqrd_model import Pqrd
from sqlalchemy import desc


def crear_pqrd(
    id_cliente, nombre, email, telefono, tipo_solicitud, asunto, descripcion
):
    nuevo_pqrd: Pqrd = Pqrd()
    nuevo_pqrd.id_cliente = id_cliente
    nuevo_pqrd.nombre = nombre
    nuevo_pqrd.email = email
    nuevo_pqrd.telefono = telefono
    nuevo_pqrd.tipo_solicitud = tipo_solicitud
    nuevo_pqrd.asunto = asunto
    nuevo_pqrd.descripcion = descripcion

    try:
        db.session.add(nuevo_pqrd)
        db.session.commit()

        return nuevo_pqrd

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al crear PQRD: {e}")


def asignar_ticket(pqrd_id, id_agente, prioridad, estado):
    try:
        Pqrd.query.filter_by(id_pqrd=pqrd_id).update(
            dict(prioridad=prioridad, estado=estado, id_agente=id_agente)
        )
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al asignar pqrd: {e}")


def cambiar_pqrd(pqrd_id, prioridad, estado):
    try:
        Pqrd.query.filter_by(id_pqrd=pqrd_id).update(
            dict(
                prioridad=prioridad,
                estado=estado,
            )
        )
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al cambiar pqrd: {e} ")


def mostrar_pqrd_cliente(id_cliente):
    try:
        pqrds_cliente = (
            Pqrd.query.filter_by(id_cliente=id_cliente)
            .order_by(desc(Pqrd.fecha_creacion))
            .all()
        )

        return pqrds_cliente
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al buscar todos pqrd-cliente: {e}")


def mostrar_pqrd_agente(id_agente):
    try:
        pqrds_agente = (
            Pqrd.query.filter_by(id_agente=id_agente)
            .order(desc(Pqrd.fecha_creacion))
            .all()
        )

        return pqrds_agente
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al buscar todos pqrd-agente: {e}")


def mostrar_todos():
    try:
        pqrds = Pqrd.query.order_by(desc(Pqrd.fecha_creacion)).all()

        return pqrds
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al mostrar todos de pqrd-admin: {e}")


def mostrar_todospqrd_empleado(id_agente):
    try:
        pqrds = (
            Pqrd.query.filter_by(id_agente=id_agente)
            .order_by(desc(Pqrd.fecha_creacion))
            .all()
        )

        return pqrds
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al mostrar todos de pqrd-empleado: {e}")


def pqrd_total_estados():
    try:
        total = Pqrd.query.order_by(desc(Pqrd.fecha_creacion)).count()

        abierto = (
            Pqrd.query.order_by(desc(Pqrd.fecha_creacion))
            .filter(Pqrd.estado == "Abierto")
            .count()
        )
        progreso = (
            Pqrd.query.order_by(desc(Pqrd.fecha_creacion))
            .filter(Pqrd.estado == "En Progreso")
            .count()
        )
        resuelto = (
            Pqrd.query.order_by(desc(Pqrd.fecha_creacion))
            .filter(Pqrd.estado == "Resuelto")
            .count()
        )

        return {
            "total": total,
            "abierto": abierto,
            "progreso": progreso,
            "resuelto": resuelto,
        }
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al mostrar estados de pqrd-admin: {e}")


def pqrd_total_estados_empleado(id_agente):
    try:
        total = (
            Pqrd.query.filter_by(id_agente=id_agente)
            .order_by(desc(Pqrd.fecha_creacion))
            .count()
        )

        abierto = (
            Pqrd.query.filter_by(id_agente=id_agente)
            .order_by(desc(Pqrd.fecha_creacion))
            .filter(Pqrd.estado == "Abierto")
            .count()
        )
        progreso = (
            Pqrd.query.filter_by(id_agente=id_agente)
            .order_by(desc(Pqrd.fecha_creacion))
            .filter(Pqrd.estado == "En Progreso")
            .count()
        )
        resuelto = (
            Pqrd.query.filter_by(id_agente=id_agente)
            .order_by(desc(Pqrd.fecha_creacion))
            .filter(Pqrd.estado == "Resuelto")
            .count()
        )

        return {
            "total": total,
            "abierto": abierto,
            "progreso": progreso,
            "resuelto": resuelto,
        }
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al mostrar estados de pqrd-empleado: {e}")


def verificar_reactivacion_chatbot():
    from datetime import datetime, timedelta

    # PQRDs escaladas hace más de 24 horas sin respuesta de técnico
    pqrd_para_reactivar = Pqrd.query.filter(
        Pqrd.es_chatbot_activo == 0,
        Pqrd.fecha_escalado <= datetime.utcnow() - timedelta(hours=24),
        Pqrd.ultima_respuesta <= datetime.utcnow() - timedelta(hours=24),
    ).all()

    for pqrd in pqrd_para_reactivar:
        pqrd.es_chatbot_activo = 1
        pqrd.fecha_reactivacion_auto = datetime.utcnow()

        # Mensaje automático
        mensaje_reactivacion = PqrdMessage(
            id_pqrd=pqrd.id_pqrd,
            id_remitente=1,
            tipo_remitente="sistema",
            mensaje="🤖 **He vuelto para ayudarte!** Como no hemos tenido respuesta del técnico, estoy aquí para continuar asisténdote. ¿En qué más puedo ayudarte?",
            es_automatico=True,
        )
        db.session.add(mensaje_reactivacion)
        print(f"✅ Reactivado chatbot para PQRD #{pqrd.id_pqrd}")

    db.session.commit()
