from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    current_app,
    send_from_directory,
    url_for,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from .models import Product
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

            try:

                db.session.add(new_product)
                db.session.commit()
                flash(f"{product_name} agregado exitosamente")
                print("Producto añadido")
                return redirect(request.url)

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
            descipcion = request.form.get("descripcion")


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

            filepath = f"./media/{unique_filename}"
            file.save(filepath)

            product = Product()
            product.product_name = product_name
            product.current_price = current_price
            product.previous_price = previous_price
            product.in_stock = stock
            product.flash_sale = flash_sale
            product.product_picture = filepath
            product.descipcion = descipcion

            try:
                Product.query.filter_by(id=item_id).update(
                    dict(
                        product_name=product_name,
                        current_price=current_price,
                        previous_price=previous_price,
                        in_stock=stock,
                        flash_sale=flash_sale,
                        product_picture=filepath,
                        descipcion=descipcion
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
                image_path = os.path.join(
                    current_app.root_path, "media", delete_product.product_picture
                )
                if os.path.exists(image_path):
                    os.remove(image_path)

            db.session.delete(delete_product)
            db.session.commit()
            flash(f"Se eliminóexitosamente ")
            print("Producto eliminado")
            return redirect(url_for("admin.ver_productos"))

        except Exception as e:
            db.session.rollback()
            flash(f"Fallo eliminación: {e}")

    return render_template("error_404.html")
