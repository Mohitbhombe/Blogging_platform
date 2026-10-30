/**
 * main.js — FlaskBlog JavaScript
 * Adds interactivity and micro-animations
 */

// ── Navbar scroll effect ───────────────────────────────────
window.addEventListener('scroll', () => {
    const nav = document.getElementById('mainNav');
    if (!nav) return;
    if (window.scrollY > 50) {
        nav.style.padding = '0.5rem 0';
        nav.style.boxShadow = '0 4px 30px rgba(0,0,0,0.3)';
    } else {
        nav.style.padding = '1rem 0';
        nav.style.boxShadow = 'none';
    }
});

// ── Animate elements on scroll (Intersection Observer) ────
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Apply fade-in animation to post cards
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.post-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    console.log('🚀 FlaskBlog initialized! Week 1 complete.');
});
