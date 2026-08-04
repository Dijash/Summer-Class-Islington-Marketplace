function getCartCookie(name) {
    const value = '; ' + document.cookie;
    const parts = value.split('; ' + name + '=');
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

function loadMiniCart() {
    fetch('/cart/api/summary/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.json())
    .then(data => {
        const itemsContainer = document.querySelector('.mini-cart-items');
        const countText = document.querySelector('.item-count-text');
        const subtotalEl = document.querySelector('.mini-cart-subtotal strong');
        const badgeEl = document.querySelector('.cart-badge');

        if (countText) countText.textContent = data.count + ' Item' + (data.count !== 1 ? 's' : '');
        if (subtotalEl) subtotalEl.textContent = '₹' + Math.round(data.subtotal).toLocaleString();
        if (badgeEl) {
            badgeEl.textContent = data.count;
            badgeEl.style.display = data.count > 0 ? 'flex' : 'none';
        }

        if (itemsContainer) {
            if (data.items.length === 0) {
                itemsContainer.innerHTML = `
                    <div class="mini-cart-empty">
                        <i class="fa-solid fa-cart-flatbed"></i>
                        <p>Your cart is empty</p>
                    </div>
                `;
            } else {
                let html = '';
                data.items.forEach(item => {
                    html += `
                        <div class="mini-cart-item" data-item-id="${item.id}">
                            <img src="${item.image}" alt="${item.title}" class="mini-cart-thumb">
                            <div class="mini-cart-details">
                                <a href="/product/${item.slug}/" class="mini-item-title">${item.title}</a>
                                <div class="mini-item-meta">
                                    ${item.size ? 'Size: ' + item.size : ''}${item.size && item.color ? ' · ' : ''}${item.color ? 'Color: ' + item.color : ''}
                                </div>
                                <div class="mini-item-price">${item.quantity} × <strong>₹${Math.round(item.price).toLocaleString()}</strong></div>
                            </div>
                            <button type="button" class="mini-item-remove" title="Remove" onclick="removeMiniCartItem(${item.id})">&times;</button>
                        </div>
                    `;
                });
                itemsContainer.innerHTML = html;
            }
        }
    });
}

function removeMiniCartItem(itemId) {
    fetch('/cart/remove/' + itemId + '/', {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            loadMiniCart();
            if (typeof showToast === 'function') showToast(data.message, 'remove');
        }
    });
}

function updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadMiniCart();
});
