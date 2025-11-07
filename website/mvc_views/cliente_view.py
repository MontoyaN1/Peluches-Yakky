from datetime import datetime
from flask import Blueprint, jsonify, render_template, request

from website.models.Pqrd.pqrd_message_model import PqrdMessage
from website.models.Pqrd.pqrd_model import Pqrd
from flask_login import current_user

from website import db
from website.models.Pqrd.pqrd_status_model import PqrdStatusHistory
from website.models.customer_model import Customer
from website.decorators import login_required


cliente_bp = Blueprint("cliente", __name__)


@cliente_bp.route("/chat/<int:pqrd_id>", methods=["GET", "POST"])
@login_required
def chat(pqrd_id):
    pqrd = Pqrd.query.filter_by(id_pqrd=pqrd_id).first_or_404()
    return render_template("pqrd_chat.html", pqrd=pqrd)


@cliente_bp.route("/enviar_mensaje/<int:pqrd_id>", methods=["POST"])
@login_required
def enviar_mensaje(pqrd_id):
    try:
        print(f"📍 INICIO - PQRD: {pqrd_id}")

        if not current_user.is_authenticated:
            return jsonify({"error": "No autenticado"}), 401

        pqrd = Pqrd.query.get(pqrd_id)
        if not pqrd:
            return jsonify({"error": "PQRD no encontrada"}), 404

        mensaje = request.form.get("mensaje")
        print(f"📍 Mensaje recibido: '{mensaje}'")

        if not mensaje or not mensaje.strip():
            return jsonify({"error": "Mensaje vacío"}), 400

        # VERIFICAR CAMPOS
        es_chatbot_activo = getattr(pqrd, "es_chatbot_activo", 1)
        mensajes_chatbot = getattr(pqrd, "mensajes_chatbot", 0)
        print(f"📍 es_chatbot_activo: {es_chatbot_activo}")
        print(f"📍 mensajes_chatbot: {mensajes_chatbot}")
        print(f"📍 Rol usuario: {current_user.rol_id}")

        # 1. Guardar mensaje usuario
        nuevo_mensaje = PqrdMessage(
            id_pqrd=pqrd.id_pqrd,
            id_remitente=current_user.id,
            tipo_remitente="cliente" if current_user.rol_id == 3 else "agente",
            mensaje=mensaje.strip(),
            es_automatico=False,
        )
        db.session.add(nuevo_mensaje)

        # 2. Procesar IA solo para clientes
        respuesta_ia = None
        if current_user.rol_id == 3 and es_chatbot_activo:
            print("📍 🤖 CLIENTE + CHATBOT ACTIVO - Procesando IA")

            try:
                from ..services.chatbot_services import DeepSeekChatBot

                chatbot = DeepSeekChatBot()

                historial = obtener_historial_para_ia(pqrd_id)

                # El historial YA está filtrado (solo cliente + sistema)
                print(f"📍 📈 Historial para IA: {len(historial)} mensajes")

                # DEBUG: Mostrar conteo real de mensajes de cliente
                mensajes_cliente = [
                    msg for msg in historial if msg["tipo"] == "cliente"
                ]
                print(
                    f"📍 👤 Mensajes de cliente en historial: {len(mensajes_cliente)}"
                )

                if chatbot.deberia_escalar_a_humano(historial):
                    print("📍 🚨 ESCALANDO A HUMANO")
                    pqrd.es_chatbot_activo = 0
                    pqrd.fecha_escalado = datetime.utcnow()
                    respuesta_ia = "🔔 **He transferido tu conversación a un técnico humano.** 🧑‍💼\n\nUn especialista se contactará contigo pronto. Gracias por tu paciencia."
                else:
                    print("📍 🧠 GENERANDO RESPUESTA CON IA")
                    respuesta_ia = chatbot.generar_respuesta(historial, pqrd)
                    print(f"📍 💬 Respuesta IA: {respuesta_ia}")

                    # Solo incrementar si fue respuesta exitosa
                    if respuesta_ia and "transferido" not in respuesta_ia.lower():
                        pqrd.mensajes_chatbot = mensajes_chatbot + 1
                        print(
                            f"📍 ✅ mensajes_chatbot incrementado a: {pqrd.mensajes_chatbot}"
                        )

            except Exception as e:
                print(f"📍 ❌ ERROR en IA: {e}")
                import traceback

                traceback.print_exc()
                respuesta_ia = "⚠️ Lo siento, hay un problema temporal con el asistente."

        elif current_user.rol_id == 3 and not es_chatbot_activo:
            print("📍 👨‍💼 CLIENTE pero CHATBOT INACTIVO - Esperando técnico")
        else:
            print("📍 🚫 No es cliente o no procesar IA")

        # 3. Guardar respuesta IA
        if respuesta_ia:
            print("📍 💾 Guardando respuesta IA en BD")
            mensaje_ia = PqrdMessage(
                id_pqrd=pqrd.id_pqrd,
                id_remitente=1,
                tipo_remitente="sistema",
                mensaje=respuesta_ia,
                es_automatico=True,
            )
            db.session.add(mensaje_ia)

        # Actualizar timestamps
        pqrd.ultima_respuesta = datetime.utcnow()
        pqrd.esperando_respuesta_de = (
            "agente" if current_user.rol_id == 3 else "cliente"
        )

        db.session.commit()
        print("📍 ✅ COMMIT EXITOSO")
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        print(f"📍 ❌ ERROR: {e}")
        import traceback

        print(f"📍 ❌ TRACEBACK: {traceback.format_exc()}")
        return jsonify({"error": "Error interno"}), 500


def obtener_historial_para_ia(pqrd_id):
    """Obtiene historial de mensajes para la IA - SOLO mensajes de cliente y sistema"""
    mensajes = (
        PqrdMessage.query.filter_by(id_pqrd=pqrd_id)
        .order_by(PqrdMessage.fecha_creacion.asc())
        .all()
    )

    # Filtrar SOLO mensajes de cliente y sistema (IA)
    historial_filtrado = [
        {
            "tipo": msg.tipo_remitente,
            "mensaje": msg.mensaje,
            "fecha": msg.fecha_creacion,
        }
        for msg in mensajes
        if msg.tipo_remitente in ["cliente", "sistema"]  # Solo estos tipos
    ]

    print(
        f"📊 Historial filtrado: {len(historial_filtrado)} mensajes (cliente + sistema)"
    )
    for i, msg in enumerate(historial_filtrado):
        print(f"   {i + 1}. [{msg['tipo']}] {msg['mensaje']}")

    return historial_filtrado


def registrar_cambio_estado(pqrd, usuario, nuevo_estado):
    """Registra cambio de estado en el historial"""
    historial = PqrdStatusHistory(
        id_pqrd=pqrd.id_pqrd,
        id_usuario=usuario.id,
        estado_anterior=pqrd.estado,
        estado_nuevo=nuevo_estado,
        comentario="Cambio automático por IA basado en conversación",
    )
    db.session.add(historial)


def notificar_escalado_a_tecnicos(pqrd):
    """Notifica a técnicos sobre una PQRD escalada"""
    # Aquí implementarías notificaciones a técnicos
    # Por ejemplo: email, websockets, notificaciones en app, etc.
    print(f"🚨 PQRD #{pqrd.id_pqrd} escalada a técnicos humanos")


@cliente_bp.route("/mensajes/<int:pqrd_id>")
@login_required
def obtener_mensajes(pqrd_id):
    try:
        print(f"🔍 DEBUG: Obteniendo mensajes para PQRD {pqrd_id}")

        # Verificar que el usuario tenga acceso a esta PQRD
        if not current_user.is_authenticated:
            return jsonify({"error": "No autenticado"}), 401

        # Verificar que la PQRD existe y el usuario tiene permisos
        pqrd = Pqrd.query.get(pqrd_id)
        if not pqrd:
            return jsonify({"error": "PQRD no encontrada"}), 404

        # Solo el cliente dueño o un agente/admin pueden ver los mensajes
        if (
            current_user.rol_id == 3 and pqrd.id_cliente != current_user.id
        ):  # Cliente normal
            return jsonify({"error": "No autorizado"}), 403

        print(
            f"🔍 DEBUG: Usuario {current_user.username} autorizado para ver PQRD {pqrd_id}"
        )

        # Obtener mensajes - VERSIÓN SIMPLIFICADA PRIMERO
        mensajes = (
            PqrdMessage.query.filter_by(id_pqrd=pqrd_id)
            .order_by(PqrdMessage.fecha_creacion.asc())
            .all()
        )

        print(f"🔍 DEBUG: Encontrados {len(mensajes)} mensajes")

        result = []
        for msg in mensajes:
            # Obtener información del remitente
            remitente = Customer.query.get(msg.id_remitente)
            if not remitente:
                continue

            # Determinar tipo y nombre para mostrar
            if remitente.rol_id in [1, 2]:  # admin o empleado
                tipo_remitente = "agente"
                if remitente.rol_id == 1:
                    display_name = f"Admin {remitente.username}"
                else:
                    display_name = f"Técnico {remitente.username}"
            else:  # cliente
                tipo_remitente = "cliente"
                if (
                    current_user.is_authenticated
                    and msg.id_remitente == current_user.id
                ):
                    display_name = "Tú"
                else:
                    display_name = f"Cliente {remitente.username}"

            result.append(
                {
                    "id": msg.id_mensaje,
                    "remitente": display_name,
                    "tipo": tipo_remitente,
                    "mensaje": msg.mensaje,
                    "fecha": msg.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                    "es_automático": msg.es_automatico,
                    "es_mio": current_user.is_authenticated
                    and msg.id_remitente == current_user.id,
                }
            )

        print(f"✅ DEBUG: Retornando {len(result)} mensajes")
        return jsonify(result)

    except Exception as e:
        print(f"❌ ERROR en obtener_mensajes: {str(e)}")
        import traceback

        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        return jsonify({"error": f"Error al cargar mensajes: {str(e)}"}), 500
