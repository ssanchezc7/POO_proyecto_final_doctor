/**
 * Gestión de formulario de asignación de permisos grupo-módulo
 * @version 1.0
 * @author Security Dome
 */

class GroupModulePermissionsForm {
    constructor() {
        this.form = null;
        this.submitBtn = null;
        this.moduleSelect = null;
        this.permissionsContainer = null;
        this.permissionCheckboxes = [];
        this.permissionItems = [];
        this.searchTimeout = null;
        
        this.init();
    }

    init() {
        console.log("🚀 Inicializando GroupModulePermissionsForm");
        
        // Esperar a que el DOM esté completamente cargado
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupElements());
        } else {
            this.setupElements();
        }
    }

    setupElements() {
        console.log("⚙️ Configurando elementos del formulario");
        
        // Obtener elementos del DOM
        this.form = document.getElementById("permissionForm");
        this.submitBtn = document.getElementById("submitBtn");
        this.moduleSelect = document.querySelector('select[name="module"]') || document.getElementById("id_module");
        this.permissionsContainer = document.getElementById("permissions-grid");
        
        console.log("📍 Elementos encontrados:");
        console.log("  - form:", this.form);
        console.log("  - submitBtn:", this.submitBtn);
        console.log("  - moduleSelect:", this.moduleSelect);
        console.log("  - permissionsContainer:", this.permissionsContainer);
        
        // Configurar event listeners
        this.setupFormSubmit();
        this.setupPermissionControls();
        this.setupModuleFilter();
        this.setupInitialState();
    }

    setupFormSubmit() {
        if (this.form && this.submitBtn) {
            this.form.addEventListener("submit", (e) => {
                this.submitBtn.disabled = true;
                this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Guardando...';

                setTimeout(() => {
                    this.submitBtn.disabled = false;
                    // El texto se restaurará según el contexto (crear/editar)
                    const isEdit = this.submitBtn.dataset.isEdit === 'true';
                    const buttonText = isEdit ? 'Actualizar Asignación' : 'Crear Asignación';
                    this.submitBtn.innerHTML = `<i class="fas fa-save mr-2"></i>${buttonText}`;
                }, 3000);
            });
        }
    }

    setupPermissionControls() {
        // Botones de selección
        const selectAllBtn = document.getElementById("select-all");
        const selectNoneBtn = document.getElementById("select-none");

        if (selectAllBtn) {
            selectAllBtn.addEventListener("click", () => {
                this.updatePermissionCheckboxes();
                this.permissionCheckboxes.forEach(checkbox => checkbox.checked = true);
                this.updatePermissionCount();
            });
        }

        if (selectNoneBtn) {
            selectNoneBtn.addEventListener("click", () => {
                this.updatePermissionCheckboxes();
                this.permissionCheckboxes.forEach(checkbox => checkbox.checked = false);
                this.updatePermissionCount();
            });
        }

        // Configurar checkboxes iniciales
        this.updatePermissionCheckboxes();
        this.permissionCheckboxes.forEach(checkbox => {
            checkbox.addEventListener("change", () => this.updatePermissionCount());
        });

        // Inicializar contador
        this.updatePermissionCount();
    }

    setupModuleFilter() {
        if (!this.moduleSelect || !this.permissionsContainer) {
            console.error("❌ No se encontraron los elementos necesarios para el filtrado");
            return;
        }

        // Event listener para cambio de módulo
        this.moduleSelect.addEventListener('change', () => {
            const moduleId = this.moduleSelect.value;
            console.log("🔄 Módulo cambiado a ID:", moduleId);
            this.loadModulePermissions(moduleId);
        });
    }

    setupInitialState() {
        // Auto-focus en el primer campo con error
        const firstError = document.querySelector(".text-red-600");
        if (firstError) {
            const errorField = firstError.closest("div").querySelector("input, select, textarea");
            if (errorField) {
                errorField.focus();
                errorField.scrollIntoView({ behavior: "smooth", block: "center" });
            }
        } else {
            const firstField = document.querySelector("#id_group");
            if (firstField) {
                firstField.focus();
            }
        }

        // Cargar permisos inicial
        const initialModule = this.moduleSelect?.value;
        console.log("🎯 Módulo inicial:", initialModule);
        if (initialModule) {
            this.loadModulePermissions(initialModule);
        } else {
            this.showSelectModuleMessage();
        }
    }

    updatePermissionCheckboxes() {
        this.permissionCheckboxes = document.querySelectorAll('input[type="checkbox"][name="permissions"]');
        this.permissionItems = document.querySelectorAll(".permission-item");
    }

    updatePermissionCount() {
        this.updatePermissionCheckboxes();
        const selectedCount = document.querySelectorAll('input[type="checkbox"][name="permissions"]:checked').length;
        const totalCount = this.permissionCheckboxes.length;

        // Actualizar contador principal
        const counter = document.getElementById("permission-counter");
        if (counter) {
            counter.textContent = `(${selectedCount} de ${totalCount} seleccionados)`;
        }

        // Actualizar texto en botones
        const selectAllBtn = document.getElementById("select-all");
        const selectNoneBtn = document.getElementById("select-none");
        
        if (selectAllBtn) {
            selectAllBtn.innerHTML = `<i class="fas fa-check-double mr-1"></i>Todos (${totalCount})`;
        }
        if (selectNoneBtn) {
            selectNoneBtn.innerHTML = `<i class="fas fa-times mr-1"></i>Ninguno`;
        }
    }

    loadModulePermissions(moduleId) {
        console.log("🔄 Cargando permisos para módulo ID:", moduleId);
        
        if (!moduleId) {
            this.showSelectModuleMessage();
            this.updatePermissionCount();
            return;
        }

        this.showLoadingMessage();

        // Construir URL (se configurará desde el template)
        const baseUrl = window.modulePermissionsUrl || '/security/ajax/get-module-permissions/';
        const url = `${baseUrl}?module_id=${moduleId}`;
        console.log("📡 Haciendo petición a:", url);

        fetch(url)
            .then(response => {
                console.log("📥 Respuesta recibida con status:", response.status);
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("📦 Datos recibidos:", data);
                this.handlePermissionsResponse(data);
            })
            .catch(error => {
                console.error("💥 Error:", error);
                this.showErrorMessage(error.message);
            });
    }

    handlePermissionsResponse(data) {
        if (data.error) {
            this.showErrorMessage(data.error);
            return;
        }

        if (!data.permissions || data.permissions.length === 0) {
            this.showNoPermissionsMessage(data.module_name || 'seleccionado');
            this.updatePermissionCount();
            return;
        }

        // Construir HTML de permisos
        let html = '';
        data.permissions.forEach(permission => {
            const permissionId = `id_permissions_${permission.id}`;
            html += `
                <div class="permission-item flex items-start space-x-2 p-2 hover:bg-white dark:hover:bg-gray-600 rounded-md">
                    <div class="flex items-center h-5">
                        <input type="checkbox" 
                               name="permissions" 
                               value="${permission.id}" 
                               id="${permissionId}"
                               class="permission-checkbox h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded dark:border-gray-600 dark:bg-gray-700 dark:focus:ring-blue-600">
                    </div>
                    <label for="${permissionId}"
                           class="text-sm text-gray-700 dark:text-gray-300 cursor-pointer flex-1">
                        <div class="font-medium">
                            ${this.escapeHtml(permission.display_name)}
                        </div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">
                            Permiso: ${this.escapeHtml(permission.codename)}
                        </div>
                    </label>
                </div>
            `;
        });

        this.permissionsContainer.innerHTML = html;

        // Re-configurar event listeners para los nuevos checkboxes
        this.updatePermissionCheckboxes();
        this.permissionCheckboxes.forEach(checkbox => {
            checkbox.addEventListener("change", () => this.updatePermissionCount());
        });

        this.updatePermissionCount();
        
        // Preservar selecciones si estamos editando
        this.preserveSelectedPermissions();
        
        console.log(`✅ ${data.permissions.length} permisos cargados exitosamente`);
    }

    preserveSelectedPermissions() {
        // Los permisos seleccionados se configurarán desde el template
        if (window.selectedPermissionIds && window.selectedPermissionIds.length > 0) {
            setTimeout(() => {
                window.selectedPermissionIds.forEach(permissionId => {
                    const checkbox = document.querySelector(`input[name="permissions"][value="${permissionId}"]`);
                    if (checkbox) {
                        checkbox.checked = true;
                    }
                });
                this.updatePermissionCount();
            }, 100);
        }
    }

    showLoadingMessage() {
        this.permissionsContainer.innerHTML = `
            <div class="col-span-full flex items-center justify-center p-8 text-gray-500">
                <i class="fas fa-spinner fa-spin mr-2"></i>
                Cargando permisos del módulo...
            </div>
        `;
    }

    showSelectModuleMessage() {
        this.permissionsContainer.innerHTML = `
            <div class="col-span-full text-center p-8">
                <div class="text-gray-400 mb-2">
                    <i class="fas fa-cube text-3xl"></i>
                </div>
                <p class="text-gray-600 dark:text-gray-400">
                    Selecciona un módulo para ver los permisos disponibles
                </p>
            </div>
        `;
    }

    showNoPermissionsMessage(moduleName) {
        this.permissionsContainer.innerHTML = `
            <div class="col-span-full text-center p-8">
                <div class="text-gray-400 mb-2">
                    <i class="fas fa-info-circle text-3xl"></i>
                </div>
                <p class="text-gray-600 dark:text-gray-400 mb-2">
                    El módulo "${this.escapeHtml(moduleName)}" no tiene permisos específicos asignados.
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-500">
                    Para asignar permisos a este módulo, ve a la gestión de módulos y configura los permisos correspondientes.
                </p>
            </div>
        `;
    }

    showErrorMessage(message) {
        this.permissionsContainer.innerHTML = `
            <div class="col-span-full text-center p-8 text-red-500">
                <i class="fas fa-exclamation-triangle text-3xl mb-2"></i>
                <p>Error: ${this.escapeHtml(message)}</p>
                <button onclick="location.reload()" 
                        class="mt-2 px-3 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600">
                    Recargar página
                </button>
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Inicializar cuando se cargue el script
document.addEventListener('DOMContentLoaded', function() {
    window.groupModulePermissionsForm = new GroupModulePermissionsForm();
});

// Exportar para uso global
window.GroupModulePermissionsForm = GroupModulePermissionsForm;