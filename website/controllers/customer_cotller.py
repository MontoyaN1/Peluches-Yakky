from website import db
from ..models.customer_model import Customer
from sqlalchemy import desc


def crear_customer(username, email, password, telefono):
    new_customer = Customer()
    new_customer.username = username
    new_customer.email = email
    new_customer.password = password
    new_customer.telefono = telefono

    try:
        db.session.add(new_customer)
        db.session.commit()

        return new_customer
    except Exception as e:
        db.session.rollback()
        return e


def validar_customer(email, password):
    customer = Customer.query.filter_by(email=email).first()

    if customer:
        if customer.verify_password(password=password):
            return customer
        else:
            return False

    else:
        raise Exception("El usaurio no existe")


def buscar_customer(customer_id):
    customer = Customer.query.get(customer_id)
    return customer


def mostrar_todos_empleados():
    try:
        empleados = (
            Customer.query.order_by(desc(Customer.date_joined))
            .filter(Customer.rol_id == 2)
            .all()
        )

        return empleados
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al mostrar todos de empleados-admin: {e}")
