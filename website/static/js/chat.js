// static/js/chat.js

let pqrdId = null;
let isLoading = false;
let lastMessageId = 0;

// Inicializar el chat
function initChat(pqrdIdFromTemplate) {
    pqrdId = pqrdIdFromTemplate;
    
    // Cargar mensajes al iniciar
    loadMessages();
    setInterval(loadMessages, 5000);
}

// Función para cargar mensajes
async function loadMessages() {
    if (isLoading || !pqrdId) return;
    isLoading = true;

    try {
        const response = await fetch(`/cliente/mensajes/${pqrdId}`);
        if (!response.ok) throw new Error(`Error: ${response.status}`);
        
        const mensajes = await response.json();
        if (!Array.isArray(mensajes)) throw new Error('Formato inválido');

        const currentLastId = mensajes.length > 0 ? mensajes[mensajes.length - 1].id : 0;
        
        if (currentLastId > lastMessageId) {
            renderMessages(mensajes);
            lastMessageId = currentLastId;
        }
    } catch (error) {
        console.error('Error cargando mensajes:', error);
        showError('Error al cargar mensajes: ' + error.message);
    }
    isLoading = false;
}

// Renderizar mensajes
function renderMessages(mensajes) {
    const chatContainer = document.getElementById('chatMessages');
    
    if (mensajes.length === 0) {
        chatContainer.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-comments fa-2x mb-3"></i>
                <p>No hay mensajes aún. Sé el primero en escribir.</p>
            </div>
        `;
        return;
    }

    chatContainer.innerHTML = mensajes.map(msg => `
        <div class="d-flex mb-3 ${msg.es_mio ? 'justify-content-end' : 'justify-content-start'}">
            <div class="message ${msg.es_mio ? 'bg-primary text-white' : 'bg-white border'} rounded-3 p-3 shadow-sm" 
                 style="max-width: 70%;">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <small class="fw-bold">${escapeHtml(msg.remitente)}</small>
                    <small class="${msg.es_mio ? 'text-white-50' : 'text-muted'}">
                        ${new Date(msg.fecha).toLocaleTimeString('es-ES', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                        })}
                    </small>
                </div>
                <div class="message-content">${escapeHtml(msg.mensaje)}</div>
            </div>
        </div>
    `).join('');

    scrollToBottom();
}

// Mostrar error
function showError(message) {
    const chatContainer = document.getElementById('chatMessages');
    chatContainer.innerHTML = `
        <div class="alert alert-danger m-3" role="alert">
            <i class="fas fa-exclamation-triangle"></i> ${escapeHtml(message)}
        </div>
    `;
}

// Enviar mensaje
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const button = document.getElementById('sendButton');
    const message = input.value.trim();

    if (!message || !pqrdId) return;

    button.disabled = true;
    input.disabled = true;

    try {
        const response = await fetch(`/cliente/enviar_mensaje/${pqrdId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `mensaje=${encodeURIComponent(message)}`
        });

        if (response.ok) {
            input.value = '';
            autoResizeTextarea();
            await loadMessages();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Error al enviar mensaje');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    }

    button.disabled = false;
    input.disabled = false;
    input.focus();
}

// Funciones auxiliares
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function insertSuggestion(text) {
    const input = document.getElementById('messageInput');
    input.value = text;
    input.focus();
    autoResizeTextarea();
}

function autoResizeTextarea() {
    const textarea = document.getElementById('messageInput');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function scrollToBottom() {
    const container = document.getElementById('chatMessages');
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Inicializar eventos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize del textarea
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('input', autoResizeTextarea);
    }
});