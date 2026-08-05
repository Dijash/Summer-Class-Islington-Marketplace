function showToast(message, type = 'success') {
    let iconClass = 'fa-solid fa-circle-check';
    let iconColor = '#10b981';
    let borderColor = '#10b981';
    let bgGradient = 'linear-gradient(135deg, #0f172a, #1e293b)';

    if (type === 'error' || type === 'danger') {
        iconClass = 'fa-solid fa-circle-exclamation';
        iconColor = '#ef4444';
        borderColor = '#ef4444';
        bgGradient = 'linear-gradient(135deg, #180d0d, #2a1212)';
    } else if (type === 'warning') {
        iconClass = 'fa-solid fa-triangle-exclamation';
        iconColor = '#f59e0b';
        borderColor = '#f59e0b';
        bgGradient = 'linear-gradient(135deg, #1c150c, #2b1f10)';
    } else if (type === 'info') {
        iconClass = 'fa-solid fa-circle-info';
        iconColor = '#3b82f6';
        borderColor = '#3b82f6';
        bgGradient = 'linear-gradient(135deg, #0f172a, #1e293b)';
    } else if (type === 'remove') {
        iconClass = 'fa-solid fa-heart-crack';
        iconColor = '#f43f5e';
        borderColor = '#f43f5e';
        bgGradient = 'linear-gradient(135deg, #1a1a2e, #16213e)';
    }

    const icon = document.createElement('i');
    icon.className = iconClass;
    icon.style.cssText = `color:${iconColor};font-size:1.15rem;margin-right:10px;flex-shrink:0;`;

    const span = document.createElement('span');
    span.textContent = message;

    const node = document.createElement('div');
    node.style.cssText = 'display:flex;align-items:center;';
    node.appendChild(icon);
    node.appendChild(span);

    if (typeof Toastify === 'function') {
        Toastify({
            node: node,
            duration: 3500,
            gravity: 'top',
            position: 'right',
            stopOnFocus: true,
            style: {
                background: bgGradient,
                borderLeft: `5px solid ${borderColor}`,
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
    } else {
        alert(message);
    }
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
