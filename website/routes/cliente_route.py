from datetime import datetime
from flask import Blueprint, jsonify, render_template, request

from ..models.pqrd.pqrd_message_model import PqrdMessage
from ..models.pqrd.pqrd_model import Pqrd
from flask_login import current_user

from website import db
from ..models.pqrd.pqrd_status_model import PqrdStatusHistory
from ..models.customer_model import Customer
from ..decorators import login_required
import requests


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

        # VERIFICAR CAMPOS (mantener igual)
        es_chatbot_activo = getattr(pqrd, "es_chatbot_activo", 1)
        mensajes_chatbot = getattr(pqrd, "mensajes_chatbot", 0)
        print(f"📍 es_chatbot_activo: {es_chatbot_activo}")
        print(f"📍 mensajes_chatbot: {mensajes_chatbot}")
        print(f"📍 Rol usuario: {current_user.rol_id}")

        # 1. Guardar mensaje usuario (mantener igual)
        nuevo_mensaje = PqrdMessage(
            id_pqrd=pqrd.id_pqrd,
            id_remitente=current_user.id,
            tipo_remitente="cliente" if current_user.rol_id == 3 else "agente",
            mensaje=mensaje.strip(),
            es_automatico=False,
        )
        db.session.add(nuevo_mensaje)

        # 2. ✅ CAMBIO PRINCIPAL: Reemplazar DeepSeek por N8N
        respuesta_ia = None
        if current_user.rol_id == 3 and (
            es_chatbot_activo or deberia_reactivar_chatbot(mensaje)
        ):
            print("📍 🤖 CLIENTE + CHATBOT ACTIVO - Enviando a N8N")

            try:
                # Preparar payload para N8N
                n8n_payload = {
                    "pqrd_id": pqrd.id_pqrd,
                    "user_message": mensaje.strip(),
                    "user_id": current_user.id,
                    "historial": obtener_historial_para_ia(
                        pqrd_id
                    ),  # Esta función SÍ se mantiene
                    "pqrd_context": {
                        "id_pqrd": pqrd.id_pqrd,
                        "asunto": pqrd.asunto,
                        "descripcion": pqrd.descripcion,
                        "tipo_solicitud": pqrd.tipo_solicitud,
                        "estado": pqrd.estado,
                        "prioridad": pqrd.prioridad,
                    },
                }

                print(f"📍 📦 Enviando a N8N: {n8n_payload}")

                # Llamar a N8N
                n8n_response = enviar_a_n8n(n8n_payload)

                if n8n_response and "respuesta" in n8n_response:
                    respuesta_ia = n8n_response["respuesta"]

                    respuesta_ia = respuesta_ia.replace("||NL||", "\n").replace(
                        "||TAB||", "\t"
                    )

                    print(f"📍 💬 Respuesta decodificada: {respuesta_ia}")

                    # Manejar escalación desde N8N
                    if n8n_response.get("escalar_a_humano"):
                        print("📍 🚨 N8N indica ESCALAR A HUMANO")
                        pqrd.es_chatbot_activo = 0
                        pqrd.fecha_escalado = datetime.utcnow()
                    elif n8n_response.get("reactivar_chatbot"):
                        print("📍 🔄 N8N indica REACTIVAR CHATBOT")
                        pqrd.es_chatbot_activo = 1
                        pqrd.fecha_reactivacion_auto = datetime.utcnow()
                    else:
                        # Incrementar contador si fue respuesta exitosa
                        pqrd.mensajes_chatbot = mensajes_chatbot + 1
                        print(
                            f"📍 ✅ mensajes_chatbot incrementado a: {pqrd.mensajes_chatbot}"
                        )

                else:
                    print("📍 ❌ N8N no respondió correctamente")
                    respuesta_ia = (
                        "⚠️ Lo siento, hay un problema temporal con el asistente."
                    )

            except Exception as e:
                print(f"📍 ❌ ERROR llamando a N8N: {e}")
                import traceback

                traceback.print_exc()
                respuesta_ia = "⚠️ Lo siento, hay un problema temporal con el asistente."

        elif current_user.rol_id == 3 and not es_chatbot_activo:
            print("📍 👨‍💼 CLIENTE pero CHATBOT INACTIVO - Esperando técnico")
        else:
            print("📍 🚫 No es cliente o no procesar IA")

        # 3. Guardar respuesta IA (mantener igual)
        if respuesta_ia:
            print(f"📍 💾 Guardando respuesta IA en BD: {respuesta_ia}")
            mensaje_ia = PqrdMessage(
                id_pqrd=pqrd.id_pqrd,
                id_remitente=1,
                tipo_remitente="sistema",
                mensaje=respuesta_ia,
                es_automatico=True,
            )
            db.session.add(mensaje_ia)

        # Actualizar timestamps (mantener igual)
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


def deberia_reactivar_chatbot(mensaje):
    """Determina si el mensaje solicita reactivar el chatbot"""
    palabras_reactivacion = [
        "bot",
        "chatbot",
        "asistente virtual",
        "volver al bot",
        "quiero el chatbot",
        "activa el bot",
        "robot",
        "asistente automático",
    ]

    mensaje_lower = mensaje.lower()
    return any(palabra in mensaje_lower for palabra in palabras_reactivacion)


def enviar_a_n8n(payload):
    """Envía el mensaje a N8N y retorna la respuesta"""
    try:
        n8n_url = "http://n8n:5678/webhook/webhook/chatbot"

        print(f"📍 🔄 Enviando a N8N: {n8n_url}")

        response = requests.post(n8n_url, json=payload, timeout=30)

        print(f"📍 📊 Status Code: {response.status_code}")
        print(f"📍 📄 Response Text: {response.text}")  # ← Ver qué devuelve realmente

        if response.status_code == 200:
            # Intentar parsear JSON
            try:
                json_response = response.json()
                print("📍 ✅ JSON parseado correctamente")
                return json_response
            except ValueError as e:
                print(f"📍 ❌ Error parseando JSON: {e}")
                return None
        else:
            print(f"📍 ❌ N8N respondió con error: {response.status_code}")
            return None

    except Exception as e:
        print(f"📍 ❌ Error enviando a N8N: {e}")
        return None


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
            "fecha": msg.fecha_creacion.isoformat(),
        }
        for msg in mensajes
        if msg.tipo_remitente in ["cliente", "sistema"]  # Solo estos tipos
    ]

    print(
        f"📊 Historial filtrado: {len(historial_filtrado)} mensajes (cliente + sistema)"
    )

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
