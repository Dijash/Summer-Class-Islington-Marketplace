function showToast(message, type = 'success') {
    const isRemove = type === 'remove';
    const icon = document.createElement('i');
    icon.className = isRemove ? 'fa-solid fa-heart-crack' : 'fa-solid fa-heart';
    icon.style.cssText = isRemove
        ? 'color:#f43f5e;font-size:1.15rem;margin-right:10px;flex-shrink:0;'
        : 'color:#e91e63;font-size:1.15rem;margin-right:10px;flex-shrink:0;';

    const span = document.createElement('span');
    span.textContent = message;

    const node = document.createElement('div');
    node.style.cssText = 'display:flex;align-items:center;';
    node.appendChild(icon);
    node.appendChild(span);

    Toastify({
        node: node,
        duration: 3000,
        gravity: 'top',
        position: 'right',
        stopOnFocus: true,
        style: {
            background: isRemove ? 'linear-gradient(135deg, #1a1a2e, #16213e)' : 'linear-gradient(135deg, #0f172a, #1e293b)',
            borderLeft: isRemove ? '5px solid #f43f5e' : '5px solid #e91e63',
            borderRadius: '10px',
            fontFamily: "'Plus Jakarta Sans', sans-serif",
            fontSize: '0.9rem',
            fontWeight: '600',
            boxShadow: '0 12px 32px rgba(0,0,0,0.3)',
            padding: '14px 20px',
            color: '#ffffff',
        },
        offset: { y: 80 },
    }).showToast();
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
