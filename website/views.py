from flask import Blueprint, jsonify, render_template, flash, redirect, request
from .models import Product, Cart, Order
from flask_login import  current_user
from website.decorators import login_required
from . import db

views = Blueprint("views", __name__)


@views.route("/")
def home():
    items_sale = Product.query.filter_by(flash_sale=True)
    return render_template(
        "home.html",
        items=items_sale,
        cart=(
            Cart.query.filter_by(customer_link=current_user.id).all()
            if current_user.is_authenticated
            else []
        ),
    )


@views.route("/agregar-carrito/<int:item_id>")
@login_required
def agregar_carrito(item_id):
    item_to_add = Product.query.get(item_id)
    item_exist = Cart.query.filter_by(
        product_link=item_id, customer_link=current_user.id
    ).first()

    if item_exist:
        try:
            item_exist.quantity = item_exist.quantity + 1
            db.session.commit()
            flash(f" La cantidad de {item_exist.product.product_name} se actualizo")
            return redirect(request.referrer)

        except Exception as e:
            print(f"Cantidad no actualizada {e}")
            flash(f" La cantidad de {item_exist.product.product_name} no actualizo")
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f"{new_cart_item.product.product_name} agregado al carrito")

    except Exception as e:
        print(f"item no añadido{e}")
        flash(f" {item_exist.product.product_name} no se agrego")

    return redirect(request.referrer)


@views.route("/carrito")
@login_required
def carrito():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    subtotal = 0
    iva = 0

    for item in cart:
        subtotal += item.product.current_price * item.quantity

    iva = subtotal * 0.19

    return render_template(
        "carrito.html", cart=cart, subtotal=subtotal, total=subtotal + iva, iva=iva
    )


@views.route("/pluscart")
@login_required
def pluscart():
    if request.method == "GET":
        cart_id = request.args.get("cart_id")

        cart_item: Cart = Cart.query.get(cart_id)
        tope = False

        if cart_item.quantity >= cart_item.product.in_stock:
            tope = True

        else:
            cart_item.quantity = cart_item.quantity + 1

        print(f"Cantidad sumando: {cart_item.quantity}")

        cart: Cart = Cart.query.filter_by(customer_link=current_user.id).all()

        db.session.commit()

        subtotal = 0
        iva = 0

        for item in cart:
            subtotal += item.product.current_price * item.quantity

        iva = subtotal * 0.19

        data = {
            "cantidad": cart_item.quantity,
            "tope": tope,
            "subtotal": subtotal,
            "total": subtotal + iva,
            "iva": iva,
        }

        return jsonify(data)


@views.route("/minuscart")
@login_required
def minuscart():
    if request.method == "GET":
        cart_id = request.args.get("cart_id")
        cart_item = Cart.query.get(cart_id)

        subtotal = 0
        iva = 0

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        if cart_item.quantity == 1:
            print("Se envia 1 como cantidad")
            cart_item.quantity = 1

        else:
            cart_item.quantity = cart_item.quantity - 1

        for item in cart:
            subtotal += item.product.current_price * item.quantity
        iva = subtotal * 0.19

        print(f"Cantidad restando: {cart_item.quantity}")
        print(f"Cantidad restando iva: {iva}")

        db.session.commit()

        data = {
            "cantidad": cart_item.quantity,
            "subtotal": subtotal,
            "total": subtotal + iva,
            "iva": iva,
        }

        return jsonify(data)


@views.route("removecart")
@login_required
def removecart():
    if request.method == "GET":
        cart_id = request.args.get("cart_id")
        cart_remove = Cart.query.get(cart_id)

        db.session.delete(cart_remove)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        subtotal = 0
        iva = 0

        for item in cart:
            subtotal += item.product.current_price * item.quantity

        iva = subtotal * 0.19

        data = {
            "cantidad": cart_remove.quantity,
            "subtotal": subtotal,
            "total": subtotal + iva,
            "iva": iva,
        }

        return jsonify(data)


@views.route("/save-order", methods=["GET", "POST"])
@login_required
def save_order():
    cart_user = Cart.query.filter_by(customer_link=current_user.id)

    if request.method == "POST":
        if cart_user:
            try:
                total = 0
                for item in cart_user:
                    total += item.product.current_price * item.quantity

                for item in cart_user:
                    new_order = Order()
                    new_order.quantity = item.quantity
                    new_order.price = item.product.current_price
                    new_order.address = request.form.get("direccion")
                    new_order.phone = request.form.get("phone")
                    new_order.forma_pago = request.form.get("forma_pago")

                    new_order.product_link = item.product_link
                    new_order.customer_link = item.customer_link

                    db.session.add(new_order)

                    product = Product.query.get(item.product_link)

                    product.in_stock -= item.quantity

                    db.session.delete(item)

                    db.session.commit()

                """ db.session.delete(cart_user)
                db.session.commit() """
                flash("Orden realizada")

                return redirect("/")

            except Exception as e:
                print(f"Error en orden: {e}")
                flash("No se pudo hacer orden")
                return redirect("/")
        else:
            flash("Tu carrito esta vacío")
            return redirect("/")

    return render_template("form-order.html")


@views.route("/pedidos")
def pedidos():
    pedidos = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template("pedidos.html", pedidos=pedidos)


@views.route("/buscar", methods=["GET", "POST"])
def buscar():
    if request.method == "POST":
        busqueda = request.form.get("buscar")
        rango_precio = request.form.get("rango_precio")

        if rango_precio:
            if rango_precio.find("-") > 0:
                inicio_str, final_str = rango_precio.split("-")
                inicio = float(inicio_str.strip())
                final = float(final_str.strip())

                productos = (
                    Product.query.filter(Product.product_name.ilike(f"%{busqueda}%"))
                    .filter(
                        Product.current_price >= inicio, Product.current_price <= final
                    )
                    .all()
                )
            else:
                rango_str = rango_precio.replace("$", "").strip()
                rango = float(rango_str)

                productos = (
                    Product.query.filter(Product.product_name.ilike(f"%{busqueda}%"))
                    .filter(Product.current_price > rango)
                    .all()
                )

        else:
            productos = Product.query.filter(
                Product.product_name.ilike(f"%{busqueda}%")
            ).all()

        return render_template(
            "buscar.html",
            productos=productos,
            cart=(
                Cart.query.filter_by(customer_link=current_user.id).all()
                if current_user.is_authenticated
                else []
            ),
            busqueda=busqueda,
        )
    return redirect("/")


@views.route("/producto/<int:item_id>")
def producto(item_id):
    producto = Product.query.get(item_id)
    return render_template(
        "producto.html",
        producto=producto,
        cart=(
            Cart.query.filter_by(customer_link=current_user.id).all()
            if current_user.is_authenticated
            else []
        ),
    )


@views.route("/productos-todo")
def productos_todos():
    productos = Product.query.all()
    return render_template(
        "productos_todo.html",
        productos=productos,
        cart=(
            Cart.query.filter_by(customer_link=current_user.id).all()
            if current_user.is_authenticated
            else []
        ),
    )



