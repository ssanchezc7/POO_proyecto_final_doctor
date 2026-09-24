document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide messages después de 5 segundos
    setTimeout(function() {
        const messages = document.querySelectorAll('[data-message-id]');
        messages.forEach(function(message) {
            closeMessage(message.dataset.messageId);
        });
    }, 5000);
});

function closeMessage(messageId) {
    const message = document.getElementById('message-' + messageId);
    if (message) {
        message.classList.add('animate-slide-out-up');
        
        // Remover del DOM después de la animación
        setTimeout(function() {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
            
            // Ocultar el contenedor si no hay más mensajes
            const container = document.getElementById('messagesContainer');
            if (container && container.children.length === 0) {
                container.classList.add('hidden');
            }
        }, 400);
    }
}

// Función para mostrar mensaje programáticamente
function showMessage(text, type = 'info') {
    const container = document.getElementById('messagesContainer');
    if (!container) return;
    
    const messageId = Date.now();
    const icons = {
        'success': 'check',
        'error': 'times', 
        'warning': 'exclamation',
        'info': 'info'
    };
    
    const typeClasses = {
        'success': 'bg-emerald-600 border-l-emerald-400 border-emerald-500 text-white shadow-emerald-900/60 dark:bg-emerald-700 dark:border-l-emerald-300 dark:border-emerald-400 dark:text-emerald-50 dark:shadow-emerald-900/80',
        'error': 'bg-red-600 border-l-red-400 border-red-500 text-white animate-shake shadow-red-900/60 dark:bg-red-700 dark:border-l-red-300 dark:border-red-400 dark:text-red-50 dark:shadow-red-900/80',
        'warning': 'bg-amber-600 border-l-amber-400 border-amber-500 text-white shadow-amber-900/60 dark:bg-amber-700 dark:border-l-amber-300 dark:border-amber-400 dark:text-amber-50 dark:shadow-amber-900/80',
        'info': 'bg-blue-600 border-l-blue-400 border-blue-500 text-white shadow-blue-900/60 dark:bg-blue-700 dark:border-l-blue-300 dark:border-blue-400 dark:text-blue-50 dark:shadow-blue-900/80'
    };
    
    const iconColors = {
        'success': 'bg-white/20 border-white/30',
        'error': 'bg-white/20 border-white/30',
        'warning': 'bg-white/20 border-white/30',
        'info': 'bg-white/20 border-white/30'
    };
    
    const messageHtml = `
        <div id="message-${messageId}" 
             class="relative mb-4 p-5 rounded-xl shadow-2xl border-l-8 border-4 overflow-hidden animate-slide-in-down backdrop-blur-sm ${typeClasses[type] || typeClasses.info}"
             data-message-id="${messageId}">
            <div class="flex items-start justify-between">
                <div class="flex items-start gap-3 flex-1">
                    <div class="flex-shrink-0 pt-0.5">
                        <div class="w-10 h-10 ${iconColors[type] || iconColors.info} rounded-full flex items-center justify-center text-white text-lg shadow-xl border-2">
                            <i class="fa-solid fa-${icons[type] || 'info'} font-bold"></i>
                        </div>
                    </div>
                    <div class="flex-1">
                        <p class="m-0 font-bold text-base leading-relaxed text-white drop-shadow-sm">${text}</p>
                    </div>
                </div>
                <button onclick="closeMessage(${messageId})" 
                        class="flex-shrink-0 ml-4 p-2 border-none bg-white/20 rounded-full cursor-pointer hover:bg-white/30 transition-all duration-200 text-white shadow-lg border-2 border-white/30">
                    <i class="fa-solid fa-times text-sm font-bold"></i>
                </button>
            </div>
            <div class="absolute bottom-0 left-0 h-2 bg-white/40 rounded-bl-xl animate-progress-bar shadow-lg"></div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', messageHtml);
    container.classList.remove('hidden');
    
    // Auto-hide después de 5 segundos
    setTimeout(() => closeMessage(messageId), 5000);
}