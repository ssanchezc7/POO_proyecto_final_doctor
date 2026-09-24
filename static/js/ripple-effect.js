// Ripple effect for buttons
document.addEventListener("DOMContentLoaded", function () {
    // Add click ripple effect to buttons
    const buttons = document.querySelectorAll("button, .btn");
    buttons.forEach((button) => {
        button.addEventListener("click", function (e) {
            if (this.disabled) return;

            const ripple = document.createElement("span");
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + "px";
            ripple.style.left = x + "px";
            ripple.style.top = y + "px";
            ripple.classList.add("ripple");

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
});