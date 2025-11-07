import os


import requests


class DeepSeekChatBot:
    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.max_messages = 5  # Aumentado a 5 mensajes mínimo
        print(f"🤖 ChatBot inicializado. API Key: {'SÍ' if self.api_key else 'NO'}")

    def deberia_escalar_a_humano(self, mensajes_historial):
        """SOLO PARA TESTING - No escalar automáticamente"""
        mensajes_cliente = [
            msg for msg in mensajes_historial if msg["tipo"] == "cliente"
        ]
        num_mensajes_cliente = len(mensajes_cliente)

        print(f"🤖 TESTING: {num_mensajes_cliente} mensajes del cliente")

        # SOLO escalar si el cliente explícitamente lo pide
        if mensajes_cliente:
            ultimo_mensaje = mensajes_cliente[-1]["mensaje"].lower()
            palabras_clave = ["técnico", "humano", "persona", "supervisor"]

            for palabra in palabras_clave:
                if palabra in ultimo_mensaje:
                    print(f"🤖 ✅ Escalando por petición explícita: '{palabra}'")
                    return True

        print("🤖 ❌ No escalar - Continuar con IA")
        return False

    def generar_respuesta(self, mensajes_historial, contexto_pqrd):
        print("🤖 Generando respuesta...")

        # Si no hay API key, usar respuestas de prueba
        if not self.api_key:
            print("🤖 Usando modo prueba (sin API key)")
            return self._respuesta_prueba(contexto_pqrd, mensajes_historial)

        try:
            # Preparar el sistema prompt
            system_prompt = self._crear_system_prompt(contexto_pqrd)

            messages = [{"role": "system", "content": system_prompt}]

            # Agregar historial (máximo 4 mensajes para contexto)
            for msg in mensajes_historial[-4:]:
                role = "user" if msg["tipo"] == "cliente" else "assistant"
                messages.append({"role": role, "content": msg["mensaje"]})

            print(f"🤖 Enviando {len(messages)} mensajes a DeepSeek API...")

            # Llamar API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            payload = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500,
            }

            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()

            result = response.json()
            respuesta = result["choices"][0]["message"]["content"]
            print("🤖 ✅ Respuesta DeepSeek obtenida")
            return respuesta

        except Exception as e:
            print(f"🤖 ❌ Error DeepSeek: {e}")
            return self._respuesta_prueba(contexto_pqrd, mensajes_historial)

    def _respuesta_prueba(self, pqrd, historial):
        """Respuestas de prueba cuando no hay API key"""
        num_mensajes = len(historial)

        if num_mensajes == 1:
            return f"👋 ¡Hola! Soy tu asistente virtual. Veo que tienes una PQRD sobre: '{pqrd.asunto}'. ¿En qué puedo ayudarte hoy?"
        elif num_mensajes == 2:
            return f"📊 El estado actual de tu solicitud #{pqrd.id_pqrd} es: {pqrd.estado}. ¿Hay algo específico que necesites saber?"
        elif num_mensajes == 3:
            return "💡 Estoy aquí para asistirte. Si necesitas hablar con un técnico humano, solo dime 'quiero hablar con una persona'."
        else:
            return "🔍 He tomado nota de tu consulta. ¿Hay algo más en lo que pueda ayudarte?"

    def _crear_system_prompt(self, pqrd):
        """Crea el prompt del sistema con contexto completo de la empresa"""

        empresa_info = """
INFORMACIÓN DE LA EMPRESA - "Peluches Yakky":
- **Nombre**: Peluches Yakky
- **Sector**: Ecommerce de venta de peluches y artesanias
- **Horario de atención**: Lunes a Viernes 8:00 AM - 6:00 PM, Sábados 9:00 AM - 1:00 PM
- **Teléfono**: +57 302 8116748
- **Email**: yakkypeluches@gmail.com
- **Sitio web**: www.peluchesyakky.com

POLÍTICAS DE ENVÍOS:
- **Cobertura**: Enviamos a todos los departamentos de Colombia
- **Tiempos de entrega**:
  * Bogotá: 1-2 días hábiles
  * Ciudades principales: 2-3 días hábiles  
  * Departamentos: 3-5 días hábiles
  * Chocó: 4-6 días hábiles
- **Costos de envío**:
  * Compras > $100.000: ENVÍO GRATIS
  * Compras < $100.000: $15.000

POLÍTICAS DE GARANTÍA:
    Todos nuestro productos como artesanias y peluches tiene garantía por un mes

DOCUMENTOS REQUERIDOS:
- **Para reclamos**: Factura, fotos del problema, descripción detallada
- **Para garantías**: Factura original, video evidenciando falla
- **Para devoluciones**: Factura, producto en empaque original

MÉTODOS DE PAGO ACEPTADOS:
- Tarjetas crédito/débito (Visa, MasterCard, American Express)
- PSE (Pagos Seguros en Línea)
- Transferencia bancaria
- Contraentrega (solo Bucaramanga)
- Nequi o Daviplata


ZONAS CON COBERTURA ESPECIAL:
- ✅ TODO Colombia incluyendo: Amazonas, Vaupés, Guainía, Chocó, Putumayo
- ❌ No entregamos en: Zonas de conflicto, áreas FARC, territorios indígenas sin acceso
"""

        return f"""
Eres un asistente virtual especializado en soporte al cliente para "PeluchesYakky".
Estás ayudando con una PQRD (Petición, Queja, Reclamo o Denuncia).

INFORMACIÓN DE LA PQRD ACTUAL:
- Número: #{pqrd.id_pqrd}
- Asunto: {pqrd.asunto}
- Descripción: {pqrd.descripcion}
- Tipo: {pqrd.tipo_solicitud}
- Estado actual: {pqrd.estado}
- Prioridad: {pqrd.prioridad}

INFORMACIÓN DE LA EMPRESA:
{empresa_info}

INSTRUCCIONES ESPECÍFICAS:
1. Responde de manera amable, profesional y EMPÁTICA
2. USA la información de la empresa para responder preguntas específicas
3. Si preguntan por envíos : CONFIRMA que sí tenemos cobertura (4-6 días hábiles, $25.000) salvo por zonas en conflicto
4. Para políticas de garantía: ESPECIFICA los tiempos según el tipo de producto
5. Para documentos: LISTA solo los requeridos según el tipo de solicitud
6. Si no sabes algo de la empresa, DI que consultarás con un especialista
7. MENCIONA números de contacto y horarios cuando sea relevante
8. Mantén las respuestas en español colombiano, sé cercano pero profesional
9. USA emojis relevantes para hacer la conversación más amigable
10. SIEMPRE ofrece ayuda adicional al final

ESTADOS DISPONIBLES:
- Abierto: Recién creado
- En proceso: Un técnico está trabajando en ello  
- Resuelto: El problema fue solucionado
- Cerrado: Finalizado completamente

RESPONDE COMO SI FUERAS UN AGENTE DE "PeluchesYakky" CON ACCESO A TODA LA INFORMACIÓN.
"""
