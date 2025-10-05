from website.models import Customer
from website import db
from datetime import datetime, timedelta
from website.mvc_models.contacto_model import Contacto
from website.mvc_models.oportunidad_model import Oportunidad
from website.mvc_models.actividad_model import Actividad

from sqlalchemy import func


def crer_empleado(nombre, correo, clave):
    empleado_nuevo: Customer = Customer()
    empleado_nuevo.username = nombre
    empleado_nuevo.email = correo
    empleado_nuevo.password = clave
    empleado_nuevo.rol_id = 2

    try:
        db.session.add(empleado_nuevo)
        db.session.commit()

        return empleado_nuevo

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear empleado: {e}")


def tasa_conversion(fecha_inicio=None, fecha_fin=None):
    if not (fecha_inicio and fecha_fin):
        fecha_inicio = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fecha_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

    # Contactos que generaron oportunidades
    contactos_con_oportunidades = (
        db.session.query(Contacto.id_contacto)
        .distinct()
        .join(Oportunidad, Oportunidad.id_contacto == Contacto.id_contacto)
        .filter(
            Oportunidad.fecha_creacion >= fecha_inicio,
            Oportunidad.fecha_creacion <= fecha_fin,
        )
        .count()
    )

    # Total contactos en el periodo
    total_contactos = Contacto.query.filter(
        Contacto.fecha_registro >= fecha_inicio, Contacto.fecha_registro <= fecha_fin
    ).count()

    print(
        f"DEBUG: Contactos con oportunidades={contactos_con_oportunidades}, Total contactos={total_contactos}"
    )

    if total_contactos == 0:
        return 0

    tasa = (contactos_con_oportunidades / total_contactos) * 100
    return round(tasa, 2)


def promedio_cliente(fecha_inicio=None, fecha_fin=None):
    if not (fecha_inicio and fecha_fin):
        fecha_inicio = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fecha_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

    resultado = (
        db.session.query(func.avg(Oportunidad.valor_estimado).label("promedio"))
        .filter(
            Oportunidad.fecha_creacion >= fecha_inicio,
            Oportunidad.fecha_creacion <= fecha_fin,
        )
        .first()
    )

    promedio = resultado[0] if resultado[0] is not None else 0

    return round(promedio, 2)


def tiempo_respuesta_actividades(fecha_inicio=None, fecha_fin=None):
    """
    Calcula el tiempo REAL de respuesta: desde que se CREA la actividad hasta que se COMPLETA
    Esta es la métrica más significativa en CRM
    """
    if not (fecha_inicio and fecha_fin):
        fecha_inicio = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fecha_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

    # Buscar actividades COMPLETADAS en el período
    actividades = Actividad.query.filter(
        Actividad.fecha_completada.isnot(None),
        Actividad.fecha_creacion.isnot(
            None
        ),  # Usar fecha_creacion en lugar de fecha_programada
        Actividad.fecha_completada >= fecha_inicio,
        Actividad.fecha_completada <= fecha_fin,
    ).all()

    print(f"=== DEBUG: {len(actividades)} actividades completadas en el período ===")

    if not actividades:
        return 0

    total_horas = 0
    actividades_validas = 0

    for actividad in actividades:
        # Tiempo real de respuesta: desde creación hasta completación
        tiempo_respuesta = actividad.fecha_completada - actividad.fecha_creacion
        horas = tiempo_respuesta.total_seconds() / 3600

        # Solo considerar tiempos positivos (deberían serlo lógicamente)
        if horas >= 0:
            total_horas += horas
            actividades_validas += 1
            print(
                f"Act {actividad.id_actividad}: Creada {actividad.fecha_creacion} -> Completada {actividad.fecha_completada} = {horas:.2f}h"
            )
        else:
            print(
                f"⚠️  Act {actividad.id_actividad}: Tiempo negativo ({horas:.2f}h) - Revisar datos"
            )

    if actividades_validas == 0:
        print("No hay actividades con tiempos de respuesta válidos")
        return 0

    promedio = total_horas / actividades_validas
    print(
        f"✅ PROMEDIO TIEMPO RESPUESTA: {promedio:.2f} horas ({actividades_validas} actividades)"
    )

    return round(promedio, 2)


def satisfaccion_promedio(fecha_inicio=None, fecha_fin=None):
    if not (fecha_inicio and fecha_fin):
        fecha_inicio = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fecha_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

    resultados = Contacto.query.filter(
        Contacto.fecha_registro.isnot(None),
        Contacto.fecha_registro >= fecha_inicio,
        Contacto.fecha_registro <= fecha_fin,
    ).all()

    if not resultados:
        return 0

    promedio = sum(contacto.satisfaccion for contacto in resultados) / len(resultados)
    return round(promedio, 2)


def ciclo_ventas_promedio(fecha_inicio=None, fecha_fin=None):
    """
    Calcula el ciclo de ventas promedio con manejo seguro de fechas
    """
    if not (fecha_inicio and fecha_fin):
        fecha_inicio = (datetime.now() - timedelta(days=90)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fecha_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

    print("=== DEBUG CICLO VENTAS ===")
    print("Rango: {fecha_inicio} a {fecha_fin}")

    # Oportunidades en CIERRE
    oportunidades = Oportunidad.query.filter(Oportunidad.etapa == "Cierre").all()

    print(f"Oportunidades en CIERRE encontradas: {len(oportunidades)}")

    if not oportunidades:
        print("No hay oportunidades en etapa Cierre")
        return 0

    total_dias = 0
    oportunidades_validas = 0

    for oportunidad in oportunidades:
        try:
            # VERIFICACIÓN SEGURA DE FECHAS
            fecha_creacion = oportunidad.fecha_creacion
            fecha_cierre = oportunidad.fecha_cierre

            print(f"Analizando OP {oportunidad.id_oportunidad}:")
            print(
                f"  - fecha_creacion: {fecha_creacion} (tipo: {type(fecha_creacion)})"
            )
            print(f"  - fecha_cierre: {fecha_cierre} (tipo: {type(fecha_cierre)})")

            # Validar que ambas fechas existan y no sean strings vacíos
            if not fecha_creacion or not fecha_cierre:
                print("  ❌ Faltan fechas - Saltando")
                continue

            # Si son strings, convertirlos a datetime
            if isinstance(fecha_creacion, str):
                if fecha_creacion.strip() == "":  # String vacío
                    print("  ❌ fecha_creacion es string vacío - Saltando")
                    continue
                try:
                    fecha_creacion = datetime.fromisoformat(
                        fecha_creacion.replace("Z", "+00:00")
                    )
                except ValueError as e:
                    print(f"  ❌ Error convirtiendo fecha_creacion: {e} - Saltando")
                    continue

            if isinstance(fecha_cierre, str):
                if fecha_cierre.strip() == "":  # String vacío
                    print("  ❌ fecha_cierre es string vacío - Saltando")
                    continue
                try:
                    fecha_cierre = datetime.fromisoformat(
                        fecha_cierre.replace("Z", "+00:00")
                    )
                except ValueError as e:
                    print(f"  ❌ Error convirtiendo fecha_cierre: {e} - Saltando")
                    continue

            # Verificar que sean objetos datetime
            if not isinstance(fecha_creacion, datetime) or not isinstance(
                fecha_cierre, datetime
            ):
                print("  ❌ Fechas no son datetime objects - Saltando")
                continue

            # Calcular ciclo
            ciclo_dias = (fecha_cierre - fecha_creacion).days

            if ciclo_dias >= 0:
                total_dias += ciclo_dias
                oportunidades_validas += 1
                print(f"  ✅ Ciclo: {ciclo_dias} días")
            else:
                print(f"  ⚠️  Ciclo negativo: {ciclo_dias} días")

        except Exception as e:
            print(f"  ❌ Error procesando OP {oportunidad.id_oportunidad}: {e}")
            continue

    if oportunidades_validas == 0:
        print("No se pudieron calcular ciclos para ninguna oportunidad")
        return 0

    promedio_dias = total_dias / oportunidades_validas
    print(
        f"🎯 CICLO VENTAS PROMEDIO: {promedio_dias:.2f} días ({oportunidades_validas} oportunidades)"
    )

    return round(promedio_dias, 2)


def metricas_retencion_simplificada(fecha_inicio=None, fecha_fin=None):
    """
    Calcula retención basada en el ESTADO de los contactos
    Retención = Contactos activos / Total contactos * 100
    """
    if not (fecha_inicio and fecha_fin):
        fecha_inicio = (datetime.now() - timedelta(days=60)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fecha_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

    print("=== DEBUG RETENCIÓN ===")
    print(f"Periodo: {fecha_inicio} a {fecha_fin}")

    # Estrategia 1: Basada en estado de contactos
    total_contactos = Contacto.query.filter(
        Contacto.fecha_registro <= fecha_fin
    ).count()

    # Contactos considerados "activos" (no en estado 'Perdido' o 'Inactivo')
    contactos_activos = Contacto.query.filter(
        Contacto.fecha_registro <= fecha_fin,
        Contacto.estado.notin_(["Perdido", "Inactivo", "Cerrado"]),
    ).count()

    print(f"Total contactos: {total_contactos}")
    print(f"Contactos activos: {contactos_activos}")

    if total_contactos == 0:
        return 0, 0

    tasa_retencion = (contactos_activos / total_contactos) * 100
    churn_rate = 100 - tasa_retencion

    print(f"Retención: {tasa_retencion:.2f}%")
    print(f"Churn Rate: {churn_rate:.2f}%")

    return round(tasa_retencion, 2), round(churn_rate, 2)


def total_contactos(fecha_inicio=None, fecha_fin=None):
    if not (fecha_inicio and fecha_fin):
        fecha_inicio = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fecha_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

    total_contactos = Contacto.query.filter(
        Contacto.fecha_registro >= fecha_inicio, Contacto.fecha_registro <= fecha_fin
    ).count()

    return total_contactos


def total_oportunidades(fecha_inicio=None, fecha_fin=None):
    if not (fecha_inicio and fecha_fin):
        fecha_inicio = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fecha_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

    total_oportunidades = Oportunidad.query.filter(
        Oportunidad.fecha_creacion >= fecha_inicio,
        Oportunidad.fecha_creacion <= fecha_fin,
    ).count()

    return total_oportunidades
