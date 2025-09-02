from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    send_from_directory,
    url_for,
)
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from .models import Order, Product, Customer
from ._init_ import db


admin = Blueprint("admin", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


@admin.route("/media/<path:filename>")
def get_image(filename):
    return send_from_directory("../media", filename)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@admin.route("/agregar-productos", methods=["GET", "POST"])
@login_required
def agregar_productos():
    if current_user.id == 1:
        if request.method == "POST":
            product_name = request.form.get("product_name")
            current_price = request.form.get("current_price")
            previous_price = request.form.get("previous_price")
            stock = request.form.get("in_stock")
            flash_sale = request.form.get("flash_sale") == "on"
            descipcion = request.form.get("descripcion")
            precio_costo = request.form.get("precio_costo")

            if "product_picture" not in request.files:
                flash("No se seleccionó ninguna imagen")
                return redirect(request.url)

            file = request.files["product_picture"]

            if file.filename == "":
                flash("No se seleccionó ninguna imagen")
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

            unique_filename = f"{datetime.now().timestamp()}_{filename}"

            filepath = os.path.join("media", unique_filename)
            file.save(filepath)

            new_product = Product()
            new_product.product_name = product_name
            new_product.current_price = current_price
            new_product.previous_price = previous_price
            new_product.in_stock = stock
            new_product.flash_sale = flash_sale
            new_product.product_picture = filepath
            new_product.descripcion = descipcion
            new_product.precio_costo = precio_costo

            try:
                db.session.add(new_product)
                db.session.commit()
                flash(f"{product_name} agregado exitosamente")
                print("Producto añadido")
                return redirect("/ver-productos")

            except Exception as e:
                db.session.rollback()
                flash(f"Fallo creación de cuenta: {e}")

        return render_template("add_produc.html")

    return render_template("error-404.html")


@admin.route("/ver-productos", methods=["GET", "POST"])
@login_required
def ver_productos():
    if current_user.id == 1:
        productos = Product.query.order_by(Product.date_added).all()
        return render_template("ver_produc.html", productos=productos)
    return render_template("error_404.html")


@admin.route("/actua-producto/<int:item_id>", methods=["GET", "POST"])
@login_required
def actua_productos(item_id):
    if current_user.id == 1:
        producto = Product.query.get(item_id)

        if request.method == "POST":
            product_name = request.form.get("product_name")
            current_price = request.form.get("current_price")
            previous_price = request.form.get("previous_price")
            stock = request.form.get("in_stock")
            flash_sale = request.form.get("flash_sale") == "on"
            descripcion = request.form.get("descripcion")
            precio_costo = request.form.get("precio_costo")

            file = request.files["product_picture"]

            exist_image = request.form.get("existing_image")

            if file.filename == "":
                filepath = exist_image

            else:
                file_remove_name = os.path.basename(exist_image)
                os.remove(f"./media/{file_remove_name}")

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)

                unique_filename = f"{datetime.now().timestamp()}_{filename}"

                filepath = f"./media/{unique_filename}"
                file.save(filepath)

            product = Product()
            product.product_name = product_name
            product.current_price = current_price
            product.previous_price = previous_price
            product.in_stock = stock
            product.flash_sale = flash_sale
            product.product_picture = filepath
            product.descripcion = descripcion
            product.precio_costo = precio_costo

            try:
                Product.query.filter_by(id=item_id).update(
                    dict(
                        product_name=product_name,
                        current_price=current_price,
                        previous_price=previous_price,
                        in_stock=stock,
                        flash_sale=flash_sale,
                        product_picture=filepath,
                        descripcion=descripcion,
                        precio_costo=precio_costo,
                    )
                )

                db.session.commit()
                flash(f"{product_name} actualizado exitosamente ")
                print("Producto actualizado")
                return redirect(url_for("admin.ver_productos"))

            except Exception as e:
                db.session.rollback()
                flash(f"Fallo creación de cuenta: {e}")
        return render_template("actua-produc.html", item=producto)
    return render_template("error_404.html")


@admin.route("/elimi-producto/<int:item_id>", methods=["GET", "POST"])
@login_required
def elimi_productos(item_id):
    if current_user.id == 1:
        try:
            delete_product = Product.query.get(item_id)

            if delete_product.product_picture:
                file_remove_name = os.path.basename(delete_product.product_picture)
                os.remove(f"./media/{file_remove_name}")

            db.session.delete(delete_product)
            db.session.commit()
            flash("Se eliminóexitosamente ")
            print("Producto eliminado")
            return redirect(url_for("admin.ver_productos"))

        except Exception as e:
            db.session.rollback()
            flash(f"Fallo eliminación: {e}")

    return render_template("error_404.html")


@admin.route("/ver-pedidos", methods=["GET", "POST"])
@login_required
def ver_pedidos():
    if current_user.id == 1:
        pedidos = Order.query.all()
        return render_template("ver_pedidos.html", pedidos=pedidos)
    return render_template("error_404.html")


@admin.route("/actua-pedido/<int:order_id>", methods=["GET", "POST"])
@login_required
def actua_pedidos(order_id):
    if current_user.id == 1:
        order = Order.query.get(order_id)
        if request.method == "POST":
            estado = request.form.get("estado")

            order = Order()
            order.status = estado

            try:
                Order.query.filter_by(id=order_id).update(dict(status=estado))

                db.session.commit()
                flash("Se actualizó correctamente estado ")
                print("Estado actualizado")
                return redirect(url_for("admin.ver_pedidos"))

            except Exception as e:
                db.session.rollback()
                flash(f"Fallo creación de cuenta: {e}")

        return render_template("actua-pedido.html", order=order)

    return render_template("error_404.html")


@admin.route("/usuarios")
@login_required
def usuarios():
    if current_user.id == 1:
        usuarios = Customer.query.filter(
            Customer.email != "admin@peluchesyakky.com"
        ).all()
        return render_template("usuarios.html", usuarios=usuarios)
    return render_template("error_404.html")


@admin.route("/adminvista")
@login_required
def adminvista():
    if current_user.id == 1:
        pedidos: Order = Order.query.all()
        return render_template("admin.html", pedidos=pedidos)
    return render_template("error_404.html")


IMPUESTO = 0.19
DESCUENTO_FLASH_SALE = 0.10
GASTOS = 300000


@admin.route("/ventas", methods=["GET", "POST"])
@login_required
def ventas():
    if current_user.id != 1:
        return render_template("error_404.html")

    # Fechas por defecto (últimos 30 días)

    fecha_inicio = (datetime.now() - timedelta(days=30)).replace(
        hour=00, minute=00, second=00, microsecond=00
    )
    fecha_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=00)

    # Verificar si se enviaron fechas desde el formulario
    if request.method == "POST":
        fecha_inicio_str = request.form.get("fecha_inicio")
        fecha_fin_str = request.form.get("fecha_fin")

        if fecha_inicio_str and fecha_fin_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
                fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
                fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
                print(f"FORM Inicio: {fecha_inicio}, fin: {fecha_fin}")

            except ValueError:
                flash("Formato de fecha incorrecto", "error")
    else:
        print(f"Inicio: {fecha_inicio}, fin: {fecha_fin}")

    # FILTRAR órdenes por el rango de fechas
    ordenes = Order.query.filter(
        Order.fecha_creacion >= fecha_inicio, Order.fecha_creacion <= fecha_fin
    ).all()

    total_ventas = 0
    total_impuestos = 0
    total_costos = 0

    """ Ventas, impuesto y descuento total """
    for orden in ordenes:
        precio_unitario = orden.price
        subtotal = precio_unitario * orden.quantity

        producto = Product.query.get(orden.product_link)
        if producto:
            descuento = DESCUENTO_FLASH_SALE if producto.flash_sale else 0.0

            total_ventas += subtotal * (1 + IMPUESTO - descuento)
            total_impuestos += subtotal * IMPUESTO
            total_costos += producto.precio_costo * orden.quantity

    """ Ventas mensuales/diarias (también filtradas por fecha) """
    resultados = (
        db.session.query(
            func.date(Order.fecha_creacion).label("dia"),
            func.sum(Order.price * Order.quantity).label("ventas"),
        )
        .filter(Order.fecha_creacion >= fecha_inicio, Order.fecha_creacion <= fecha_fin)
        .group_by("dia")
        .order_by("dia")
        .all()
    )

    dias = []
    ventas_diarias = []

    for dia, ventas in resultados:
        dia_dt = datetime.strptime(str(dia), "%Y-%m-%d")
        dia_bonito = dia_dt.strftime("%d %b")
        dias.append(dia_bonito)
        ventas_diarias.append(float(ventas) if ventas else 0.0)

    print(f"ventas: {total_ventas}, costos: {total_costos} y gastos: {GASTOS}")

    utilidad = total_ventas - (total_costos + GASTOS)

    print(f"Utilidad: {utilidad}")

    # Formatear fechas para mostrar en el template
    fecha_inicio_formatted = fecha_inicio.strftime("%Y-%m-%d")
    fecha_fin_formatted = fecha_fin.strftime("%Y-%m-%d")
    hoy_formatted = datetime.now().strftime("%A, %B %d, %Y")

    return render_template(
        "ventas.html",
        total_ventas=round(total_ventas, 2),
        total_impuestos=round(total_impuestos, 2),
        impuesto=IMPUESTO,
        dias=dias,
        ventas_diarias=ventas_diarias,
        hoy=hoy_formatted,
        total_costos=round(total_costos, 2),
        utilidad=round(utilidad, 2),
        fecha_inicio=fecha_inicio_formatted,
        fecha_fin=fecha_fin_formatted,
    )
