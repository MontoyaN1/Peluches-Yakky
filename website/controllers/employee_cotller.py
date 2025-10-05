from website import db
from website.mvc_models.contacto_model import Contacto
from website.mvc_models.interaccion_model import Interaccion
from website.mvc_models.oportunidad_model import Oportunidad
from website.mvc_models.actividad_model import Actividad
from datetime import datetime
from sqlalchemy import desc


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
        contactos = Contacto.query.order_by(desc(Contacto.fecha_registro)).all()

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
        actividades = Actividad.query.order_by(desc(Actividad.fecha_programada)).all()

        return actividades

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear actividad: {e}")
        raise Exception(f"Error al buscar todos actividades: {e}")


def todos_actividades_empleado():
    try:
        actividades = (
            Actividad.query.filter(Actividad.estado != "Completado")
            .order_by(desc(Actividad.fecha_programada))
            .all()
        )

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
    try:
        contactos_totales = Contacto.query.filter(
            Contacto.id_agente == id_agente
        ).count()
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

    except Exception as e:
        db.session.rollback()
        print(f"Erros en las metricas: {e}")
        raise Exception("Error en las métricas")


def buscar_contacto(id_contacto):
    try:
        contacto: Contacto = Contacto.query.get(id_contacto)
        return contacto

    except Exception as e:
        raise Exception(f"Error buscar contacto: {e}")


def buscar_oportunidad(id_oportunidad):
    try:
        oportunidad: Oportunidad = Oportunidad.query.get(id_oportunidad)
        return oportunidad

    except Exception as e:
        raise Exception(f"Error buscar oportunidad: {e}")


def buscar_actividad(id_actividad):
    try:
        actividad: Actividad = Actividad.query.get(id_actividad)
        return actividad

    except Exception as e:
        raise Exception(f"Error buscar actividad: {e}")


def buscar_interaccion(id_interaccion):
    try:
        interaccion: Interaccion = Interaccion.query.get(id_interaccion)
        return interaccion

    except Exception as e:
        raise Exception(f"Error buscar interaccion: {e}")


def actualizar_contacto(id_contacto, nombre, email, telefono, empresa, canal, estado,satisfaccion):
    try:
        Contacto.query.filter_by(id_contacto=id_contacto).update(
            dict(
                nombre=nombre,
                email=email,
                telefono=telefono,
                empresa=empresa,
                canal=canal,
                estado=estado,
                satisfaccion=satisfaccion
            )
        )

        db.session.commit()

        print("Contacto actualizado")
        return True

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al actualizar contacto: {e}")


def actualizar_oportunidad(
    id_oportunidad, titulo, valor_estimado, etapa, probabilidad, descripcion
):
    try:
        Oportunidad.query.filter_by(id_oportunidad=id_oportunidad).update(
            dict(
                titulo=titulo,
                valor_estimado=valor_estimado,
                etapa=etapa,
                probabilidad=probabilidad,
                descripcion=descripcion,
            )
        )

        db.session.commit()

        print("Oportunidad actualizado")
        return True

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al actualizar oportunidad: {e}")


def actualizar_actividad(
    id_actividad, tipo_actividad, titulo, descripcion, fecha_programada, estado
):
    try:
        if estado == "Completado":
            fecha_completada = datetime.utcnow()
            Actividad.query.filter_by(id_actividad=id_actividad).update(
                dict(fecha_completada=fecha_completada)
            )
        fecha_programada = datetime.strptime(fecha_programada, "%Y-%m-%dT%H:%M")

        Actividad.query.filter_by(id_actividad=id_actividad).update(
            dict(
                tipo_actividad=tipo_actividad,
                titulo=titulo,
                descripcion=descripcion,
                fecha_programada=fecha_programada,
                estado=estado,
            )
        )

        db.session.commit()

        print("Actividad actualizado")
        return True

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al actualizar actividad: {e}")


def actualizar_interaccion(id_interaccion, tipo_interaccion, descripcion, resultado):
    try:
        Interaccion.query.filter_by(id_interaccion=id_interaccion).update(
            dict(
                tipo_interaccion=tipo_interaccion,
                descripcion=descripcion,
                resultado=resultado,
            )
        )

        db.session.commit()

        print("Interaccion actualizada")
        return True

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al actualizar interaccion: {e}")
