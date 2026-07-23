// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateThemeIcon('dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        updateThemeIcon('light');
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const iconSpan = document.getElementById('theme-icon');
    if (iconSpan) {
        iconSpan.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    updateCartBadge();
    renderCartItems();
});

function getCart() {
    return JSON.parse(localStorage.getItem('fh_cart')) || [];
}

function saveCart(cart) {
    localStorage.setItem('fh_cart', JSON.stringify(cart));
    updateCartBadge();
}

function addToCart(id, name, price, image) {
    const cart = getCart();
    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ id, name, price, image, quantity: 1 });
    }
    saveCart(cart);
    alert(`Added ${name} to your cart!`);
}

function updateCartBadge() {
    const cart = getCart();
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    const badge = document.getElementById('cart-count');
    if (badge) {
        badge.innerText = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

function removeFromCart(id) {
    let cart = getCart();
    cart = cart.filter(item => item.id !== id);
    saveCart(cart);
    renderCartItems();
}

function updateQuantity(id, change) {
    const cart = getCart();
    const item = cart.find(i => i.id === id);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(id);
            return;
        }
    }
    saveCart(cart);
    renderCartItems();
}

function formatPrice(price) {
    return 'LKR ' + parseFloat(price).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}

function renderCartItems() {
    const container = document.getElementById('cart-items-container');
    const totalElem = document.getElementById('cart-total-price');
    if (!container) return;

    const cart = getCart();
    
    if (cart.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 2rem;">Your cart is empty. <br><br> <a href="/shop" class="btn-primary" style="display:inline-block">Go Shopping</a></p>';
        if(totalElem) totalElem.innerText = 'LKR 0.00';
        return;
    }

    let html = '';
    let total = 0;

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        html += `
            <div class="cart-item-ui glass">
                <img src="${item.image}" alt="${item.name}" style="width: 80px; height: 80px; object-fit: contain; border-radius: 0.5rem; background: rgba(255,255,255,0.05);">
                <div style="flex: 1;">
                    <h4 style="margin-bottom: 0.25rem;">${item.name}</h4>
                    <div style="color: var(--primary); font-weight: bold;">${formatPrice(item.price)}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <button onclick="updateQuantity(${item.id}, -1)" class="btn-primary" style="padding: 0.25rem 0.75rem;">-</button>
                    <span>${item.quantity}</span>
                    <button onclick="updateQuantity(${item.id}, 1)" class="btn-primary" style="padding: 0.25rem 0.75rem;">+</button>
                </div>
                <button onclick="removeFromCart(${item.id})" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 1.5rem; transition: transform 0.2s; padding: 0.5rem;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">&times;</button>
            </div>
        `;
    });

    container.innerHTML = html;
    if(totalElem) totalElem.innerText = formatPrice(total);
}

function placeOrderWhatsApp() {
    const cart = getCart();
    if (cart.length === 0) {
        alert("Your cart is empty!");
        return;
    }

    let message = "Hello, I would like to place an order from FH Online Store:%0A%0A";
    let total = 0;
    
    cart.forEach(item => {
        message += `* ${item.quantity}x ${item.name} - ${formatPrice(item.price)}%0A`;
        total += item.price * item.quantity;
    });

    message += `%0A*Total: ${formatPrice(total)}*%0A%0APlease let me know the payment and delivery details.`;
    
    const phone = "94754738475";
    const url = `https://api.whatsapp.com/send?phone=${phone}&text=${message}`;
    
    // Clear cart after placing order
    localStorage.removeItem('fh_cart');
    updateCartBadge();
    renderCartItems();
    
    window.open(url, '_blank');
}
