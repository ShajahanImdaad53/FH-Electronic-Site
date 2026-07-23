// animation.js - E-commerce Animations
class EcommerceAnimations {
    constructor() {
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.productCardAnimations();
        this.navbarAnimations();
        this.scrollAnimations();
        this.cartAnimations();
        this.loadingAnimations();
        this.imageZoom();
    }

    // Product hover effects
    productCardAnimations() {
        document.querySelectorAll('.product-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-8px)';
                card.style.boxShadow = '0 15px 30px rgba(0,0,0,0.15)';
                card.querySelector('.product-image').style.transform = 'scale(1.05)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
                card.querySelector('.product-image').style.transform = 'scale(1)';
            });
        });
    }

    // Navbar scroll effects
    navbarAnimations() {
        const navbar = document.querySelector('header') || document.querySelector('.navbar');
        if (!navbar) return;
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(255, 255, 255, 0.95)';
                navbar.style.backdropFilter = 'blur(10px)';
                navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.1)';
            } else {
                navbar.style.background = '';
                navbar.style.backdropFilter = '';
                navbar.style.boxShadow = '';
            }
        });
    }

    // Scroll reveal animations
    scrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('.product-section, .feature-card').forEach(el => {
            el.classList.add('fade-up');
            observer.observe(el);
        });
    }

    // Add to cart animation
    cartAnimations() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-to-cart')) {
                const btn = e.target.closest('.add-to-cart');
                const originalText = btn.innerHTML;
                
                btn.innerHTML = '<i class="fas fa-check"></i> Added!';
                btn.style.background = '#10b981';
                
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.background = '';
                }, 1500);
            }
        });
    }

    // Loading animations
    loadingAnimations() {
        window.addEventListener('load', () => {
            document.body.classList.add('loaded');
        });
    }

    // Image zoom on hover
    imageZoom() {
        document.querySelectorAll('.product-image').forEach(img => {
            img.addEventListener('mouseenter', () => {
                img.style.transform = 'scale(1.1)';
                img.style.transition = 'transform 0.5s ease';
            });
            
            img.addEventListener('mouseleave', () => {
                img.style.transform = 'scale(1)';
            });
        });
    }
}

// Initialize animations
new EcommerceAnimations();