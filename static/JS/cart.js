// cart.js - Shopping Cart Management
class ShoppingCart {
    constructor() {
        this.cart = JSON.parse(localStorage.getItem('ecommerce_cart')) || [];
        this.init();
    }

    init() {
        this.updateCartCount();
        this.setupEventListeners();
        this.loadCartItems();
    }

    // Add item to cart
    addItem(product) {
        const existingItem = this.cart.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += product.quantity || 1;
        } else {
            this.cart.push({
                ...product,
                quantity: product.quantity || 1
            });
        }
        
        this.saveCart();
        this.updateCartCount();
        this.showNotification(`${product.name} added to cart!`);
    }

    // Remove item from cart
    removeItem(productId) {
        this.cart = this.cart.filter(item => item.id !== productId);
        this.saveCart();
        this.updateCartCount();
        this.loadCartItems();
    }

    // Update item quantity
    updateQuantity(productId, quantity) {
        const item = this.cart.find(item => item.id === productId);
        if (item) {
            item.quantity = Math.max(1, quantity);
            this.saveCart();
            this.updateCartCount();
            this.loadCartItems();
        }
    }

    // Calculate total price
    calculateTotal() {
        return this.cart.reduce((total, item) => {
            return total + (item.price * item.quantity);
        }, 0).toFixed(2);
    }

    // Get cart count
    getCartCount() {
        return this.cart.reduce((count, item) => count + item.quantity, 0);
    }

    // Update cart count display
    updateCartCount() {
        const countElements = document.querySelectorAll('.cart-count');
        const count = this.getCartCount();
        
        countElements.forEach(element => {
            element.textContent = count;
            element.style.display = count > 0 ? 'inline-block' : 'none';
        });
    }

    // Load cart items in cart page
    loadCartItems() {
        const cartContainer = document.getElementById('cart-items');
        const cartTotal = document.getElementById('cart-total');
        
        if (!cartContainer) return;
        
        if (this.cart.length === 0) {
            cartContainer.innerHTML = `
                <div class="empty-cart">
                    <i class="fas fa-shopping-cart"></i>
                    <h3>Your cart is empty</h3>
                    <p>Add some products to get started!</p>
                    <a href="products.html" class="btn btn-primary">Shop Now</a>
                </div>
            `;
            if (cartTotal) cartTotal.textContent = '0.00';
            return;
        }
        
        let html = '';
        this.cart.forEach(item => {
            html += `
                <div class="cart-item" data-id="${item.id}">
                    <img src="${item.image || 'placeholder.jpg'}" alt="${item.name}">
                    <div class="cart-item-details">
                        <h4>${item.name}</h4>
                        <p>$${item.price.toFixed(2)}</p>
                    </div>
                    <div class="cart-item-quantity">
                        <button class="quantity-btn minus" onclick="cart.updateQuantity('${item.id}', ${item.quantity - 1})">-</button>
                        <span>${item.quantity}</span>
                        <button class="quantity-btn plus" onclick="cart.updateQuantity('${item.id}', ${item.quantity + 1})">+</button>
                    </div>
                    <div class="cart-item-total">
                        $${(item.price * item.quantity).toFixed(2)}
                    </div>
                    <button class="remove-item" onclick="cart.removeItem('${item.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        });
        
        cartContainer.innerHTML = html;
        if (cartTotal) cartTotal.textContent = this.calculateTotal();
    }

    // Checkout process
    checkout() {
        if (this.cart.length === 0) {
            alert('Your cart is empty!');
            return;
        }
        
        // In a real application, this would redirect to a payment gateway
        const orderData = {
            items: this.cart,
            total: this.calculateTotal(),
            timestamp: new Date().toISOString(),
            orderId: 'ORD' + Date.now()
        };
        
        console.log('Checkout initiated:', orderData);
        
        // Simulate order processing
        alert(`Order placed successfully! Total: $${this.calculateTotal()}`);
        
        // Clear cart after checkout
        this.cart = [];
        this.saveCart();
        this.updateCartCount();
        this.loadCartItems();
        
        // Redirect to confirmation page
        // window.location.href = 'order-confirmation.html';
    }

    // Save cart to localStorage
    saveCart() {
        localStorage.setItem('ecommerce_cart', JSON.stringify(this.cart));
    }

    // Show notification
    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    // Event listeners
    setupEventListeners() {
        // Add to cart buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-to-cart')) {
                const button = e.target.closest('.add-to-cart');
                const product = {
                    id: button.dataset.id || 'prod_' + Date.now(),
                    name: button.dataset.name || 'Product',
                    price: parseFloat(button.dataset.price) || 0,
                    image: button.dataset.image || ''
                };
                this.addItem(product);
            }
        });
        
        // Checkout button
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => this.checkout());
        }
    }
}

// Initialize cart globally
const cart = new ShoppingCart();