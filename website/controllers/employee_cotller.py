from website import db
from website.mvc_models.contacto_model import Contacto
from website.mvc_models.interaccion_model import Interaccion
from website.mvc_models.oportunidad_model import Oportunidad
from website.mvc_models.actividad_model import Actividad
from datetime import datetime


def crear_contacto(nombre, email, telefono, empresa, canal, id_agente):
    try:
        contacto_existente = Contacto.query.filter_by(email=email).first()
        if contacto_existente:
            raise Exception("Correo ya esta registrado")

        nuevo_contacto = Contacto(
            nombre=nombre,
            email=email,
            telefono=telefono,
            empresa=empresa,
            canal=canal,
            id_agente=id_agente,
        )

        db.session.add(nuevo_contacto)
        db.session.commit()
        return nuevo_contacto

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear contacto: {e}")
        raise Exception(e)


def crear_interaccion(
    id_contacto,
    id_agente,
    tipo_interaccion,
    descripcion,
    resultado,
    id_oportunidad=None,
    id_actividad=None,
):
    try:
        nuevo_interaccion: Interaccion = Interaccion(
            id_contacto=id_contacto,
            id_agente=id_agente,
            tipo_interaccion=tipo_interaccion,
            descripcion=descripcion,
            resultado=resultado,
            id_oportunidad=id_oportunidad,
            id_actividad=id_actividad,
        )

        db.session.add(nuevo_interaccion)
        db.session.commit()
        return nuevo_interaccion

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear interaccion: {e}")
        return None


def crear_oportunidad(
    id_contacto, id_agente, titulo, valor_estimado, probabilidad, descripcion
):
    try:
        nuevo_oportunidad: Oportunidad = Oportunidad(
            id_contacto=id_contacto,
            id_agente=id_agente,
            titulo=titulo,
            valor_estimado=valor_estimado,
            probabilidad=probabilidad,
            descripcion=descripcion,
        )

        db.session.add(nuevo_oportunidad)
        db.session.commit()
        return nuevo_oportunidad

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear oportunidad: {e}")
        raise Exception(f"Error al crear oportunidad: {e}")


def crear_actividad(
    id_contacto,
    id_oportunidad,
    id_agente,
    titulo,
    tipo_actividad,
    fecha_programada,
    descripcion,
):
    try:
        fecha_programada = datetime.strptime(fecha_programada, "%Y-%m-%dT%H:%M")

        nueva_actividad: Actividad = Actividad(
            id_contacto=id_contacto,
            id_oportunidad=id_oportunidad,
            id_agente=id_agente,
            titulo=titulo,
            tipo_actividad=tipo_actividad,
            fecha_programada=fecha_programada,
            descripcion=descripcion,
        )

        db.session.add(nueva_actividad)
        db.session.commit()
        return nueva_actividad

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear actividad: {e}")
        raise Exception(f"Error al crear actividad: {e}")


def todos_contactos():
    try:
        contactos = Contacto.query.order_by(Contacto.fecha_registro).all()

        return contactos

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear actividad: {e}")
        raise Exception(f"Error al buscar todos contactos: {e}")


def todos_oportunidades():
    try:
        oportunidades = (
            Oportunidad.query.filter(Oportunidad.etapa != "Cierre")
            .order_by(Oportunidad.fecha_creacion)
            .all()
        )

        return oportunidades

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear actividad: {e}")
        raise Exception(f"Error al buscar todos oportunidades: {e}")


def todos_oportunidades_sin_filtro():
    try:
        oportunidades = Oportunidad.query.order_by(Oportunidad.fecha_creacion).all()

        return oportunidades

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear actividad: {e}")
        raise Exception(f"Error al buscar todos oportunidades: {e}")


def todos_actividades():
    try:
        actividades = Actividad.query.order_by(Actividad.fecha_programada).all()

        return actividades

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear actividad: {e}")
        raise Exception(f"Error al buscar todos actividades: {e}")


def todos_interacciones():
    try:
        interacciones = Interaccion.query.order_by(Interaccion.fecha_interaccion).all()

        return interacciones

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear actividad: {e}")
        raise Exception(f"Error al buscar todos interaciones: {e}")


def metricas_empleado(id_agente):
    contactos_totales = Contacto.query.filter(Contacto.id_agente == id_agente).count()
    oportunidades_totales = Oportunidad.query.filter(
        Oportunidad.id_agente == id_agente
    ).count()
    actividades_totales = Actividad.query.filter(
        Actividad.id_agente == id_agente, Actividad.estado == "Pendiente"
    ).count()

    respuesta = {
        "contactos": contactos_totales,
        "oportunidades": oportunidades_totales,
        "actividades": actividades_totales,
    }

    return respuesta


def buscar_contacto(id_contacto):
    pass
