function openDeleteModal(url, description) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const descriptionElement = document.getElementById('Description');
    
    if (modal && form && descriptionElement) {
        form.action = url;
        descriptionElement.textContent = description;
        modal.classList.remove('hidden');
        
        // Agregar animación de entrada
        setTimeout(() => {
            modal.classList.add('animate-fade-in');
        }, 10);
    }
}

function closeModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.classList.add('animate-fade-out');
        
        setTimeout(() => {
            modal.classList.add('hidden');
            modal.classList.remove('animate-fade-in', 'animate-fade-out');
        }, 200);
    }
}

// Cerrar modal al hacer clic fuera del contenido
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    // Cerrar modal con la tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
});