document.addEventListener('DOMContentLoaded', function() {
    // User dropdown functionality
    const userDropdown = document.getElementById('userDropdown');
    const userDropdownMenu = document.getElementById('userDropdownMenu');
    const userDropdownIcon = document.getElementById('userDropdownIcon');
    
    if (userDropdown && userDropdownMenu) {
        userDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isVisible = !userDropdownMenu.classList.contains('opacity-0');
            
            if (isVisible) {
                // Hide dropdown
                userDropdownMenu.classList.add('opacity-0', 'invisible', 'scale-95');
                userDropdownMenu.classList.remove('opacity-100', 'visible', 'scale-100');
                if (userDropdownIcon) userDropdownIcon.classList.remove('rotate-180');
            } else {
                // Show dropdown
                userDropdownMenu.classList.remove('opacity-0', 'invisible', 'scale-95');
                userDropdownMenu.classList.add('opacity-100', 'visible', 'scale-100');
                if (userDropdownIcon) userDropdownIcon.classList.add('rotate-180');
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userDropdown.contains(e.target) && !userDropdownMenu.contains(e.target)) {
                userDropdownMenu.classList.add('opacity-0', 'invisible', 'scale-95');
                userDropdownMenu.classList.remove('opacity-100', 'visible', 'scale-100');
                if (userDropdownIcon) userDropdownIcon.classList.remove('rotate-180');
            }
        });

        // Prevent dropdown from closing when clicking inside
        userDropdownMenu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // Groups selector functionality (desktop and mobile)
    function handleGroupChange(selector) {
        if (selector) {
            selector.addEventListener('change', function() {
                const selectedGroup = this.value;
                
                if (selectedGroup) {
                    // Preserve current URL path but add/update gpid parameter
                    const currentUrl = new URL(window.location.href);
                    currentUrl.searchParams.set('gpid', selectedGroup);
                    window.location.href = currentUrl.toString();
                } else {
                    // Remove gpid parameter if no group selected
                    const currentUrl = new URL(window.location.href);
                    currentUrl.searchParams.delete('gpid');
                    window.location.href = currentUrl.toString();
                }
            });
        }
    }

    // Initialize group selectors
    const groupSelects = document.querySelectorAll('#groupSelect, #mobileGroupSelect');
    groupSelects.forEach(select => {
        handleGroupChange(select);
        
        // Ensure both selectors stay synchronized
        select.addEventListener('change', function() {
            const selectedValue = this.value;
            groupSelects.forEach(otherSelect => {
                if (otherSelect !== this) {
                    otherSelect.value = selectedValue;
                }
            });
        });
    });

    // Mobile menu functionality (placeholder for future implementation)
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            // Toggle mobile menu if needed
            console.log('Mobile menu clicked');
        });
    }
});