from website.models import Customer
from website import db


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
