/* Chatbot Widget - Funcionalidad avanzada */

class ChatbotWidget {
    constructor() {
        this.isOpen = false;
        this.isMinimized = false;
        this.isRecording = false;
        this.recognition = null;
        this.currentConversationId = null;
        this.messageHistory = [];
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initSpeechRecognition();
        this.loadChatbotPosition();
        this.preloadResponses();
    }
    
    preloadResponses() {
        // Respuestas rápidas predefinidas
        this.quickResponses = [
            "¿Cuántos pacientes hay registrados?",
            "Muestra las citas de hoy",
            "¿Qué medicamentos tienen stock bajo?",
            "Estadísticas del mes",
            "Buscar paciente por cédula"
        ];
    }
    
    setupEventListeners() {
        // Toggle chatbot
        document.getElementById('chatbotToggle').addEventListener('click', () => {
            this.toggleChatbot();
        });
        
        // Minimize/Close
        document.getElementById('chatbotMinimize').addEventListener('click', () => {
            this.minimizeChatbot();
        });
        
        document.getElementById('chatbotClose').addEventListener('click', () => {
            this.closeChatbot();
        });
        
        // Send message
        document.getElementById('chatbotSendBtn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        document.getElementById('chatbotInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        // Voice recognition
        document.getElementById('chatbotVoiceBtn').addEventListener('click', () => {
            this.toggleVoiceRecognition();
        });
        
        // Auto-resize text area
        document.getElementById('chatbotInput').addEventListener('input', (e) => {
            this.autoResizeInput(e.target);
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                this.openChatbot();
                document.getElementById('chatbotInput').focus();
            }
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChatbot();
            }
        });
        
        // Drag functionality
        this.makeDraggable();
        
        // Notification badge
        this.setupNotifications();
    }
    
    autoResizeInput(input) {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    }
    
    setupNotifications() {
        // Simular notificaciones de nuevos mensajes importantes
        setInterval(() => {
            if (!this.isOpen && Math.random() < 0.1) { // 10% de probabilidad cada minuto
                this.showNotificationBadge();
            }
        }, 60000); // Cada minuto
    }
    
    showNotificationBadge() {
        const toggle = document.getElementById('chatbotToggle');
        const badge = document.createElement('div');
        badge.className = 'notification-badge';
        badge.textContent = '!';
        toggle.appendChild(badge);
        
        setTimeout(() => {
            if (badge.parentNode) {
                badge.parentNode.removeChild(badge);
            }
        }, 5000);
    }
    
    toggleChatbot() {
        if (this.isOpen) {
            this.closeChatbot();
        } else {
            this.openChatbot();
        }
    }
    
    openChatbot() {
        const toggle = document.getElementById('chatbotToggle');
        const window = document.getElementById('chatbotWindow');
        
        this.isOpen = true;
        this.isMinimized = false;
        
        toggle.classList.add('active');
        window.classList.add('show');
        window.classList.remove('minimized');
        
        // Remover badge de notificación
        const badge = toggle.querySelector('.notification-badge');
        if (badge) {
            badge.remove();
        }
        
        // Focus input con delay para animación
        setTimeout(() => {
            document.getElementById('chatbotInput').focus();
        }, 300);
        
        // Scroll al final
        this.scrollToBottom();
    }
    
    closeChatbot() {
        const toggle = document.getElementById('chatbotToggle');
        const window = document.getElementById('chatbotWindow');
        
        this.isOpen = false;
        this.isMinimized = false;
        
        toggle.classList.remove('active');
        window.classList.remove('show');
        window.classList.remove('minimized');
        
        // Detener reconocimiento de voz si está activo
        if (this.isRecording) {
            this.recognition.stop();
        }
    }
    
    minimizeChatbot() {
        const window = document.getElementById('chatbotWindow');
        
        this.isMinimized = !this.isMinimized;
        
        if (this.isMinimized) {
            window.classList.add('minimized');
        } else {
            window.classList.remove('minimized');
            setTimeout(() => {
                document.getElementById('chatbotInput').focus();
            }, 100);
        }
    }
    
    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.lang = 'es-ES';
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.maxAlternatives = 1;
            
            this.recognition.onstart = () => {
                this.isRecording = true;
                this.updateVoiceButton();
                this.showVoiceStatus();
                this.addSystemMessage('🎤 Escuchando... Habla ahora');
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const confidence = event.results[0][0].confidence;
                
                document.getElementById('chatbotInput').value = transcript;
                this.hideVoiceStatus();
                
                if (confidence > 0.7) {
                    this.addSystemMessage(`✅ Mensaje capturado: "${transcript}"`);
                    setTimeout(() => this.sendMessage(), 500);
                } else {
                    this.addSystemMessage(`⚠️ Mensaje poco claro. Por favor escríbelo o intenta de nuevo.`);
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('Error de reconocimiento de voz:', event.error);
                this.hideVoiceStatus();
                this.isRecording = false;
                this.updateVoiceButton();
                
                let errorMessage = 'Error al capturar voz.';
                switch(event.error) {
                    case 'no-speech':
                        errorMessage = 'No se detectó voz. Intenta de nuevo.';
                        break;
                    case 'audio-capture':
                        errorMessage = 'Error con el micrófono.';
                        break;
                    case 'not-allowed':
                        errorMessage = 'Micrófono no permitido. Verifica permisos.';
                        break;
                }
                this.addSystemMessage(`❌ ${errorMessage}`);
            };
            
            this.recognition.onend = () => {
                this.isRecording = false;
                this.updateVoiceButton();
                this.hideVoiceStatus();
            };
        } else {
            console.warn('Reconocimiento de voz no soportado');
            document.getElementById('chatbotVoiceBtn').style.display = 'none';
        }
    }
    
    toggleVoiceRecognition() {
        if (!this.recognition) return;
        
        if (this.isRecording) {
            this.recognition.stop();
        } else {
            try {
                this.recognition.start();
            } catch (error) {
                console.error('Error iniciando reconocimiento de voz:', error);
                this.addSystemMessage('❌ Error iniciando reconocimiento de voz');
            }
        }
    }
    
    updateVoiceButton() {
        const voiceBtn = document.getElementById('chatbotVoiceBtn');
        if (this.isRecording) {
            voiceBtn.classList.add('recording');
            voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
            voiceBtn.title = 'Detener grabación';
        } else {
            voiceBtn.classList.remove('recording');
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceBtn.title = 'Hablar (mantén presionado)';
        }
    }
    
    showVoiceStatus() {
        const status = document.getElementById('chatbotVoiceStatus');
        status.classList.add('show');
    }
    
    hideVoiceStatus() {
        const status = document.getElementById('chatbotVoiceStatus');
        status.classList.remove('show');
    }
    
    async sendMessage() {
        const input = document.getElementById('chatbotInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Deshabilitar input temporalmente
        input.disabled = true;
        document.getElementById('chatbotSendBtn').disabled = true;
        
        // Mostrar mensaje del usuario
        this.addMessage(message, 'user');
        this.messageHistory.push({type: 'user', message: message});
        input.value = '';
        input.style.height = 'auto';
        
        // Mostrar indicador de escritura
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/chatbot/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.currentConversationId
                })
            });
            
            const data = await response.json();
            
            this.hideTypingIndicator();
            
            if (data.success) {
                this.addMessage(data.response, 'bot');
                this.messageHistory.push({type: 'bot', message: data.response});
                this.currentConversationId = data.conversation_id;
                
                // Mostrar contexto si está disponible
                if (data.context && Object.keys(data.context).length > 0) {
                    console.log('Contexto médico:', data.context);
                    this.showContextData(data.context);
                }
            } else {
                this.addMessage('❌ ' + data.error, 'bot', true);
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('❌ Error de conexión. Por favor intenta nuevamente.', 'bot', true);
            console.error('Error:', error);
        } finally {
            // Rehabilitar input
            input.disabled = false;
            document.getElementById('chatbotSendBtn').disabled = false;
            input.focus();
        }
    }
    
    addMessage(text, sender, isError = false) {
        const messagesContainer = document.getElementById('chatbotMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        let bubbleClass = 'message-bubble';
        
        if (isError) {
            bubbleClass += ' error-message';
        } else if (sender === 'system') {
            bubbleClass += ' system-message';
        }
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="${bubbleClass}">${this.formatMessage(text)}</div>
        `;
        
        // Insertar antes del indicador de escritura
        const typingIndicator = messagesContainer.querySelector('.typing-indicator');
        messagesContainer.insertBefore(messageDiv, typingIndicator);
        
        // Scroll al final
        this.scrollToBottom();
        
        // Efecto de aparición
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        setTimeout(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 50);
    }
    
    addSystemMessage(text) {
        this.addMessage(text, 'system');
        setTimeout(() => {
            const systemMessages = document.querySelectorAll('.message.system');
            systemMessages.forEach(msg => {
                if (msg.textContent.includes(text.substring(0, 10))) {
                    msg.style.opacity = '0';
                    setTimeout(() => msg.remove(), 300);
                }
            });
        }, 3000);
    }
    
    showContextData(context) {
        // Mostrar datos del contexto de manera visual
        if (context.estadisticas) {
            const stats = context.estadisticas;
            let statsMessage = '📊 **Estadísticas actuales:**\n\n';
            for (const [key, value] of Object.entries(stats)) {
                statsMessage += `• ${key.replace('_', ' ')}: **${value}**\n`;
            }
            this.addMessage(statsMessage, 'bot');
        }
    }
    
    formatMessage(text) {
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/^•\s/gm, '<span class="bullet">•</span> ');
    }
    
    showTypingIndicator() {
        const indicator = document.querySelector('#chatbotMessages .typing-indicator');
        indicator.classList.add('show');
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const indicator = document.querySelector('#chatbotMessages .typing-indicator');
        indicator.classList.remove('show');
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbotMessages');
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }
    
    makeDraggable() {
        const header = document.querySelector('.chatbot-header');
        const widget = document.getElementById('chatbotWidget');
        let isDragging = false;
        let startX, startY, startRight, startBottom;
        
        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            
            const rect = widget.getBoundingClientRect();
            startRight = window.innerWidth - rect.right;
            startBottom = window.innerHeight - rect.bottom;
            
            header.style.cursor = 'grabbing';
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });
        
        function onMouseMove(e) {
            if (!isDragging) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            const newRight = startRight - deltaX;
            const newBottom = startBottom - deltaY;
            
            widget.style.right = Math.max(0, Math.min(newRight, window.innerWidth - 100)) + 'px';
            widget.style.bottom = Math.max(0, Math.min(newBottom, window.innerHeight - 100)) + 'px';
        }
        
        function onMouseUp() {
            isDragging = false;
            header.style.cursor = 'move';
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            
            // Guardar posición
            const rect = widget.getBoundingClientRect();
            localStorage.setItem('chatbotPosition', JSON.stringify({
                right: window.innerWidth - rect.right,
                bottom: window.innerHeight - rect.bottom
            }));
        }
    }
    
    loadChatbotPosition() {
        const savedPosition = localStorage.getItem('chatbotPosition');
        if (savedPosition) {
            const { right, bottom } = JSON.parse(savedPosition);
            const widget = document.getElementById('chatbotWidget');
            widget.style.right = right + 'px';
            widget.style.bottom = bottom + 'px';
        }
    }
    
    getCsrfToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }
}

// Funciones de utilidad
window.chatbotUtils = {
    insertQuickResponse: function(text) {
        document.getElementById('chatbotInput').value = text;
        document.getElementById('chatbotInput').focus();
    },
    
    clearChat: function() {
        const messagesContainer = document.getElementById('chatbotMessages');
        const messages = messagesContainer.querySelectorAll('.message:not(.typing-indicator)');
        messages.forEach(msg => {
            if (!msg.querySelector('.message-bubble').textContent.includes('¡Hola! Soy tu asistente')) {
                msg.remove();
            }
        });
    }
};

// Inicializar el widget cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    window.chatbotWidget = new ChatbotWidget();
    console.log('🤖 ChatBot Widget inicializado - Presiona Ctrl+K para abrir');
});
