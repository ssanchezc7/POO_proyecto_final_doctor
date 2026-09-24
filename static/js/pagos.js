/**
 * JavaScript para el módulo de pagos
 * Maneja interacciones, validaciones y efectos visuales
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar tooltips si Bootstrap está disponible
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Formateo automático de campos de moneda
    const moneyInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    moneyInputs.forEach(input => {
        // Formatear al cargar
        if (input.value) {
            formatMoney(input);
        }
        
        // Formatear al cambiar
        input.addEventListener('blur', function() {
            formatMoney(this);
        });
        
        // Validar entrada
        input.addEventListener('input', function() {
            validateMoneyInput(this);
        });
    });
    
    // Auto-submit de formularios de búsqueda
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        const searchInputs = searchForm.querySelectorAll('select, input[type="date"]');
        searchInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Agregar un pequeño delay para mejor UX
                setTimeout(() => {
                    searchForm.submit();
                }, 300);
            });
        });
    }
    
    // Confirmaciones de acciones críticas
    const criticalActions = document.querySelectorAll('[data-action="delete"], [data-action="cancel-payment"]');
    criticalActions.forEach(element => {
        element.addEventListener('click', function(e) {
            const action = this.getAttribute('data-action');
            const confirmMessage = getConfirmMessage(action);
            
            if (!confirm(confirmMessage)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Efectos de loading en botones
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            showLoadingState(this);
        });
    });
    
    // Auto-cálculo de subtotales en formularios de detalle
    initializeSubtotalCalculation();
    
    // Actualización automática de estados de pago
    initializePaymentStatusUpdates();
    
    // Animaciones de entrada para las tarjetas
    animateCards();
    
    // Manejo de copiar al portapapeles
    initializeCopyToClipboard();
});

/**
 * Formatea un campo de entrada de dinero
 */
function formatMoney(input) {
    const value = parseFloat(input.value);
    if (!isNaN(value)) {
        input.value = value.toFixed(2);
    }
}

/**
 * Valida entrada de dinero en tiempo real
 */
function validateMoneyInput(input) {
    let value = input.value;
    
    // Remover caracteres no válidos
    value = value.replace(/[^\d.]/g, '');
    
    // Asegurar solo un punto decimal
    const parts = value.split('.');
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }
    
    // Limitar decimales a 2 dígitos
    if (parts[1] && parts[1].length > 2) {
        value = parts[0] + '.' + parts[1].substring(0, 2);
    }
    
    input.value = value;
}

/**
 * Obtiene mensaje de confirmación basado en la acción
 */
function getConfirmMessage(action) {
    const messages = {
        'delete': '¿Estás seguro de que deseas eliminar este elemento? Esta acción no se puede deshacer.',
        'cancel-payment': '¿Estás seguro de que deseas cancelar este pago?',
        'default': '¿Estás seguro de que deseas continuar?'
    };
    
    return messages[action] || messages['default'];
}

/**
 * Muestra estado de carga en un botón
 */
function showLoadingState(button) {
    const originalText = button.innerHTML;
    const loadingText = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
    
    button.innerHTML = loadingText;
    button.disabled = true;
    
    // Restaurar después de 10 segundos como fallback
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 10000);
}

/**
 * Inicializa el cálculo automático de subtotales
 */
function initializeSubtotalCalculation() {
    const cantidadInput = document.getElementById('id_cantidad');
    const precioInput = document.getElementById('id_precio_unitario');
    const subtotalDisplay = document.getElementById('subtotalDisplay');
    
    if (cantidadInput && precioInput && subtotalDisplay) {
        function calculateSubtotal() {
            const cantidad = parseFloat(cantidadInput.value) || 0;
            const precio = parseFloat(precioInput.value) || 0;
            const subtotal = cantidad * precio;
            
            subtotalDisplay.textContent = '$' + subtotal.toFixed(2);
            
            // Cambiar color basado en el valor
            if (subtotal > 0) {
                subtotalDisplay.className = 'subtotal-display text-success';
            } else {
                subtotalDisplay.className = 'subtotal-display text-muted';
            }
        }
        
        cantidadInput.addEventListener('input', calculateSubtotal);
        precioInput.addEventListener('input', calculateSubtotal);
        
        // Cálculo inicial
        calculateSubtotal();
    }
}

/**
 * Inicializa las actualizaciones automáticas de estado de pago
 */
function initializePaymentStatusUpdates() {
    const statusForms = document.querySelectorAll('form[action*="actualizar-estado"]');
    
    statusForms.forEach(form => {
        const select = form.querySelector('select');
        if (select) {
            select.addEventListener('change', function() {
                const newStatus = this.options[this.selectedIndex].text;
                if (confirm(`¿Cambiar el estado del pago a "${newStatus}"?`)) {
                    form.submit();
                } else {
                    // Revertir selección
                    this.selectedIndex = this.getAttribute('data-original-index') || 0;
                }
            });
            
            // Guardar índice original
            select.setAttribute('data-original-index', select.selectedIndex);
        }
    });
}

/**
 * Anima las tarjetas al cargar la página
 */
function animateCards() {
    const cards = document.querySelectorAll('.payment-card, .payment-detail-card');
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * Inicializa la funcionalidad de copiar al portapapeles
 */
function initializeCopyToClipboard() {
    const copyButtons = document.querySelectorAll('[data-copy]');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            
            navigator.clipboard.writeText(textToCopy).then(() => {
                showToast('Copiado al portapapeles', 'success');
            }).catch(() => {
                // Fallback para navegadores antiguos
                const textArea = document.createElement('textarea');
                textArea.value = textToCopy;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                showToast('Copiado al portapapeles', 'success');
            });
        });
    });
}

/**
 * Muestra un toast de notificación
 */
function showToast(message, type = 'info') {
    // Si existe un sistema de toasts (como Bootstrap), úsalo
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : 'primary'} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        // Crear contenedor si no existe
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remover después de que se oculte
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    } else {
        // Fallback simple
        alert(message);
    }
}

/**
 * Funciones utilitarias para PayPal
 */
const PayPalUtils = {
    /**
     * Valida que el pago esté listo para PayPal
     */
    validatePayment: function(pagoId, total) {
        if (!pagoId || !total || total <= 0) {
            showToast('Datos de pago inválidos', 'error');
            return false;
        }
        return true;
    },
    
    /**
     * Muestra el estado de carga para PayPal
     */
    showPayPalLoading: function() {
        const paypalButtons = document.querySelectorAll('.paypal-btn, .paypal-button');
        paypalButtons.forEach(btn => {
            btn.innerHTML = '<i class="fab fa-paypal me-2"></i>Conectando con PayPal...';
            btn.disabled = true;
        });
    },
    
    /**
     * Restaura los botones de PayPal
     */
    restorePayPalButtons: function() {
        const paypalButtons = document.querySelectorAll('.paypal-btn, .paypal-button');
        paypalButtons.forEach(btn => {
            btn.innerHTML = '<i class="fab fa-paypal me-2"></i>Pagar con PayPal';
            btn.disabled = false;
        });
    }
};

/**
 * Manejo de errores globales para el módulo de pagos
 */
window.addEventListener('error', function(e) {
    console.error('Error en módulo de pagos:', e.error);
    
    // Solo mostrar errores relevantes al usuario
    if (e.error && e.error.message && e.error.message.includes('paypal')) {
        showToast('Error en el procesamiento de PayPal. Por favor, intenta nuevamente.', 'error');
    }
});

/**
 * Funciones expuestas globalmente
 */
window.PagosModule = {
    formatMoney: formatMoney,
    validateMoneyInput: validateMoneyInput,
    showToast: showToast,
    PayPalUtils: PayPalUtils
};
