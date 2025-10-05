from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from flask_login import current_user
from website.controllers.employee_cotller import (
    crear_contacto,
    crear_interaccion,
    crear_oportunidad,
    crear_actividad,
    todos_contactos,
    todos_oportunidades,
    todos_oportunidades_sin_filtro,
    todos_actividades,
    todos_actividades_empleado,
    todos_interacciones,
    metricas_empleado,
    buscar_contacto,
    actualizar_contacto,
    buscar_oportunidad,
    actualizar_oportunidad,
    buscar_actividad,
    actualizar_actividad,
    buscar_interaccion,
    actualizar_interaccion,
)
from website.decorators import rol_required, login_required


employee = Blueprint("employee", __name__)


@employee.route("/")
@login_required
@rol_required(2)
def empleado_vista():
    try:
        contactos = todos_contactos()
        oportunidades = todos_oportunidades()
        actividades = todos_actividades()
        metricas = metricas_empleado(current_user.id)

        return render_template(
            "employee.html",
            contactos=contactos,
            oportunidades=oportunidades,
            actividades=actividades,
            metricas=metricas,
        )
    except Exception as e:
        flash(e)
        raise Exception(f"Error al mostrar datos {e}")


@employee.route("/crear_contacto", methods=["GET", "POST"])
@login_required
@rol_required(2)
def crear_contacto_vista():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        celular = request.form.get("celular")
        empresa = request.form.get("empresa")
        canal = request.form.get("canal")

        try:
            nuevo_contacto = crear_contacto(
                nombre, email, celular, empresa, canal, current_user.id
            )

        except Exception as e:
            flash(f"Error: {e}")
            return render_template("employee.html")

        if nuevo_contacto:
            session["id_contacto"] = nuevo_contacto.id_contacto

            flash("Contacto creado correctamente")

            return render_template(
                "crear_contacto.html",
                creado=True,
            )
        else:
            flash("Error al crear usuario")

        return render_template("employee.html")

    return render_template("crear_contacto.html", creado=False)


@employee.route("/crear-interaccion", methods=["GET", "POST"])
@login_required
@rol_required(2)
def crear_interaccion_vista():
    if request.method == "POST":
        interaccion = request.form.get("interaccion")
        descripcion = request.form.get("descripcion")
        resultado = request.form.get("resultado")

        id_contacto = session.get("id_contacto")
        id_oportunidad = session.get("id_oportunidad")
        id_actividad = session.get("id_actividad")

        id_agente = current_user.id

        try:
            nueva_interaccion = crear_interaccion(
                id_contacto=id_contacto,
                id_agente=id_agente,
                tipo_interaccion=interaccion,
                descripcion=descripcion,
                resultado=resultado,
                id_oportunidad=id_oportunidad,
                id_actividad=id_actividad,
            )

            if nueva_interaccion:
                flash("Interacción creada correctamente")
                return redirect(url_for("employee.empleado_vista"))
        except Exception as e:
            flash(e)
            return redirect(url_for("employee.empleado_vista"))

        return render_template("employee.html")

    return render_template("crear_interaccion.html", creado=False)


@employee.route("/crear-oportunidad", methods=["GET", "POST"])
@login_required
@rol_required(2)
def crear_oportunidad_vista():
    if request.method == "POST":
        titulo = request.form.get("titulo")
        valor_estimado = request.form.get("estimado")
        probabilidad = request.form.get("probabilidad")
        descripcion = request.form.get("descripcion")

        id_agente = current_user.id
        id_contacto = session.get("id_contacto")

        try:
            nueva_oportunidad = crear_oportunidad(
                id_contacto=id_contacto,
                id_agente=id_agente,
                titulo=titulo,
                valor_estimado=valor_estimado,
                probabilidad=probabilidad,
                descripcion=descripcion,
            )

        except Exception as e:
            flash(f"{e}")
            return render_template("employee.html")

        if nueva_oportunidad:
            session["id_oportunidad"] = nueva_oportunidad.id_oportunidad

            flash("Oportunidad creada correctamente")

            return render_template("crear_oportunidad.html", creado=True)
        else:
            flash("Error al crear Oportunidad")

        return render_template("employee.html")

    return render_template("crear_oportunidad.html", creado=False)


@employee.route("/crear-actividad", methods=["GET", "POST"])
@login_required
@rol_required(2)
def crear_actividad_vista():
    if request.method == "POST":
        titulo = request.form.get("titulo")
        tipo_actividad = request.form.get("actividad")
        fecha_programada = request.form.get("fecha")
        descripcion = request.form.get("descripcion")

        id_agente = current_user.id
        id_contacto = session.get("id_contacto")
        id_oportunidad = session.get("id_oportunidad")

        try:
            nueva_actividad = crear_actividad(
                id_contacto=id_contacto,
                id_oportunidad=id_oportunidad,
                id_agente=id_agente,
                titulo=titulo,
                tipo_actividad=tipo_actividad,
                fecha_programada=fecha_programada,
                descripcion=descripcion,
            )

            if nueva_actividad:
                flash("Actividad creada correctamente")

                return redirect(url_for("employee.crear_interaccion_vista"))
        except Exception as e:
            flash(f"{e}")
            return redirect("/empleado")

    return render_template("crear_actividad.html")


@employee.route("/tabla-contactos")
@login_required
@rol_required(2)
def tabla_contactos():
    contactos = todos_contactos()

    return render_template("tabla_contactos.html", contactos=contactos)


@employee.route("/tabla-oportunidades")
@login_required
@rol_required(2)
def tabla_oportunidades():
    oportunidades = todos_oportunidades_sin_filtro()

    return render_template("tabla_oportunidades.html", oportunidades=oportunidades)


@employee.route("/tabla-actividades")
@login_required
@rol_required(2)
def tabla_actividades():
    actividades = todos_actividades_empleado()

    return render_template("tabla_actividades.html", actividades=actividades)


@employee.route("/tabla-interacciones")
@login_required
@rol_required(2)
def tabla_interacciones():
    interacciones = todos_interacciones()

    return render_template("tabla_interacciones.html", interacciones=interacciones)


@employee.route("/editar-contacto/<int:id_contacto>", methods=["GET", "POST"])
@login_required
@rol_required(2)
def editar_contacto(id_contacto):
    contacto = buscar_contacto(id_contacto)

    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        telefono = request.form.get("telefono")
        empresa = request.form.get("empresa")
        canal = request.form.get("canal")
        estado = request.form.get("estado")
        satisfaccion = request.form.get("satisfaccion")

        try:
            contacto_editado = actualizar_contacto(
                id_contacto=id_contacto,
                nombre=nombre,
                email=email,
                telefono=telefono,
                empresa=empresa,
                canal=canal,
                estado=estado,
                satisfaccion=satisfaccion,
            )

            if contacto_editado:
                flash("Contacto actualizado")
                return redirect(url_for("employee.tabla_contactos"))
        except Exception as e:
            flash(e)
            print(e)
            return redirect(url_for("employee.tabla_contactos"))

    return render_template("editar_contacto.html", contacto=contacto)


@employee.route("/editar-oportunidad/<int:id_oportunidad>", methods=["GET", "POST"])
@login_required
@rol_required(2)
def editar_oportunidad(id_oportunidad):
    oportunidad = buscar_oportunidad(id_oportunidad=id_oportunidad)

    if request.method == "POST":
        titulo = request.form.get("titulo")
        valor_estimado = request.form.get("valor_estimado")
        probabilidad = request.form.get("probabilidad")
        etapa = request.form.get("etapa")
        descripcion = request.form.get("descripcion")

        try:
            oportunidad_editada = actualizar_oportunidad(
                id_oportunidad=id_oportunidad,
                titulo=titulo,
                valor_estimado=valor_estimado,
                etapa=etapa,
                probabilidad=probabilidad,
                descripcion=descripcion,
            )
            if oportunidad_editada:
                flash("Oportunidad actualizado")
                return redirect(url_for("employee.tabla_oportunidades"))
        except Exception as e:
            flash(e)
            print(e)
            return redirect(url_for("employee.tabla_oportunidades"))

    return render_template("editar_oportunidad.html", oportunidad=oportunidad)


@employee.route("/editar-actividad/<int:id_actividad>", methods=["GET", "POST"])
@login_required
@rol_required(2)
def editar_actividad(id_actividad):
    actividad = buscar_actividad(id_actividad=id_actividad)

    if request.method == "POST":
        titulo = request.form.get("titulo")
        tipo_actividad = request.form.get("actividad")
        descripcion = request.form.get("descripcion")
        fecha_programda = request.form.get("fecha")
        estado = request.form.get("estado")

        try:
            actividad_actualizada = actualizar_actividad(
                id_actividad=id_actividad,
                tipo_actividad=tipo_actividad,
                titulo=titulo,
                descripcion=descripcion,
                fecha_programada=fecha_programda,
                estado=estado,
            )
            if actividad_actualizada:
                flash("Actividad actualizado")
                return redirect(url_for("employee.tabla_actividades"))
        except Exception as e:
            flash(f"Error: {e}")
            print(e)
            return redirect(url_for("employee.tabla_actividades"))

    return render_template("editar_actividad.html", actividad=actividad)
