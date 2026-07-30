function showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast-item ${type === 'remove' ? 'toast-remove' : ''}`;
    
    const iconClass = type === 'remove' ? 'fa-solid fa-heart-crack' : 'fa-solid fa-heart';
    toast.innerHTML = `<i class="${iconClass} toast-icon"></i><span>${message}</span>`;
    
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

function togglePasswordVisibility(btn) {
    if (!btn) return;
    const container = btn.closest('.input-with-icon') || btn.closest('.form-group');
    if (!container) return;
    const input = container.querySelector('input[type="password"], input[type="text"]');
    const icon = btn.querySelector('i');
    if (!input) return;

    if (input.type === 'password') {
        input.type = 'text';
        if (icon) {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        }
    } else {
        input.type = 'password';
        if (icon) {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
}
