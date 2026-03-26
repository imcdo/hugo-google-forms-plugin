document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('hugo-google-form');
    const toastContainer = document.getElementById('toast-container');

    const showToast = (message, type = 'success') => {
        const toast = document.createElement('div');
        const bgColor = type === 'success' ? 'bg-green-600' : 'bg-red-600';
        toast.className = `${bgColor} text-white px-6 py-3 rounded shadow-lg transition-opacity duration-500 mb-2`;
        toast.innerText = message;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 500);
        }, 4000);
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        let isValid = true;
        let missingFields = [];

        // 1. Validation Logic
        form.querySelectorAll('[data-required="true"]').forEach(field => {
            if (field.classList.contains('radio-group') || field.classList.contains('rating-group')) {
                const name = field.getAttribute('data-name');
                if (!form.querySelector(`input[name="${name}"]:checked`)) {
                    isValid = false;
                    missingFields.push(field.previousElementSibling.innerText.replace(' *', ''));
                }
            } else if (!field.value.trim()) {
                isValid = false;
                missingFields.push(field.previousElementSibling.innerText.replace(' *', ''));
            }
        });

        if (!isValid) {
            showToast(`Missing: ${missingFields.join(', ')}`, 'error');
            return;
        }

        // 2. AJAX Submission (No-CORS)
        const formData = new FormData(form);
        try {
            await fetch(form.action, {
                method: 'POST',
                body: formData,
                mode: 'no-cors'
            });
            
            showToast("Submitted successfully!");
            form.reset();
        } catch (error) {
            showToast("Submission failed. Check your connection.", "error");
        }
    });
});