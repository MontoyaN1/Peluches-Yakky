from flask import Blueprint, render_template, request, flash, session
from flask_login import current_user, login_required
from website.controllers.employee_cotller import (
    crear_contacto,
    crear_interaccion,
    crear_oportunidad,
    crear_actividad,
    todos_contactos,
    todos_oportunidades,
    todos_oportunidades_sin_filtro,
    todos_actividades,
    todos_interacciones,
    metricas_empleado,
)


employee = Blueprint("employee", __name__)


@login_required
@employee.route("/")
def empleado_vista():
    if current_user.rol_id != 2:
        return render_template("home.html")
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


@login_required
@employee.route("/crear_contacto", methods=["GET", "POST"])
def crear_contacto_vista():
    if current_user.rol_id != 2:
        return render_template("home.html")
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


@login_required
@employee.route("/crear-interaccion", methods=["GET", "POST"])
def crear_interaccion_vista():
    if current_user.rol_id != 2:
        return render_template("home.html")
    if request.method == "POST":
        interaccion = request.form.get("interaccion")
        descripcion = request.form.get("descripcion")
        resultado = request.form.get("resultado")

        id_contacto = session.get("id_contacto")
        id_oportunidad = session.get("id_oportunidad")
        id_actividad = session.get("id_actividad")

        id_agente = current_user.id

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
        else:
            flash("Error al guardar la interacción")

        return render_template("employee.html")

    return render_template("crear_interaccion.html", creado=False)


@login_required
@employee.route("/crear-oportunidad", methods=["GET", "POST"])
def crear_oportunidad_vista():
    if current_user.rol_id != 2:
        return render_template("home.html")
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


@login_required
@employee.route("/crear-actividad", methods=["GET", "POST"])
def crear_actividad_vista():
    if current_user.rol_id != 2:
        return render_template("home.html")
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
        except Exception as e:
            flash(f"{e}")
            return render_template("employee.html")

        if nueva_actividad:
            flash("Actividad creada correctamente")

            return render_template("employee.html")
        else:
            flash("Error al crear Actividad")

        return render_template("employee.html")

    return render_template("crear_actividad.html")


@login_required
@employee.route("/tabla-contactos")
def tabla_contacos():
    if current_user.rol_id != 2:
        return render_template("home.html")

    contactos = todos_contactos()

    return render_template("tabla_contactos.html", contactos=contactos)


@login_required
@employee.route("/tabla-oportunidades")
def tabla_oportunidades():
    if current_user.rol_id != 2:
        return render_template("home.html")

    oportunidades = todos_oportunidades_sin_filtro()

    return render_template("tabla_oportunidades.html", oportunidades=oportunidades)


@login_required
@employee.route("/tabla-actividades")
def tabla_actividades():
    if current_user.rol_id != 2:
        return render_template("home.html")

    actividades = todos_actividades()

    return render_template("tabla_actividades.html", actividades=actividades)


@login_required
@employee.route("/tabla-interacciones")
def tabla_interacciones():
    if current_user.rol_id != 2:
        return render_template("home.html")

    interacciones = todos_interacciones()

    return render_template("tabla_interacciones.html", interacciones=interacciones)



@login_required
@employee.route("/editar-contacto/<int:id_contacto>",methods=["GET","POST"])
def editar_contacto(id_contacto):
    if current_user.rol_id != 2:
        return render_template("home.html")

    

    return render_template("editar_contacto.html")
