/* ═══════════════════════════════════════════════════════════════════════════════
   FIX MY ITCH — Animation System
   Scroll-driven reveals · Parallax · Magnetic interactions · Counters
   ═══════════════════════════════════════════════════════════════════════════════ */

'use strict';

/* ── ScrollAnimator ────────────────────────────────────────────────────────── */
class ScrollAnimator {
  /**
   * Observes elements with animation classes and adds `.visible`
   * when they enter the viewport.
   *
   * @param {Object} options
   * @param {number} options.threshold  — Intersection ratio to trigger (0-1)
   * @param {string} options.rootMargin — IntersectionObserver rootMargin
   */
  constructor({ threshold = 0.15, rootMargin = '0px 0px -40px 0px' } = {}) {
    this.selectors = [
      '.fade-up',
      '.fade-in',
      '.slide-left',
      '.slide-right',
      '.scale-in',
    ];

    this.observer = new IntersectionObserver(
      (entries) => this._handleIntersect(entries),
      { threshold, rootMargin }
    );

    this._observe();
  }

  /** Gather all target elements and begin observing. */
  _observe() {
    const selector = this.selectors.join(', ');
    const elements = document.querySelectorAll(selector);

    elements.forEach((el) => {
      // Honour a data-delay attribute for custom stagger
      const delay = el.dataset.delay;
      if (delay) {
        el.style.transitionDelay = `${delay}ms`;
      }
      this.observer.observe(el);
    });
  }

  /** Callback — add `.visible` once and stop observing. */
  _handleIntersect(entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        this.observer.unobserve(entry.target);
      }
    });
  }

  /** Tear down the observer cleanly. */
  destroy() {
    this.observer.disconnect();
  }
}


/* ── TextRevealer ──────────────────────────────────────────────────────────── */
class TextRevealer {
  /**
   * Progressive word-by-word text reveal for elements with
   * `.text-reveal-words`. Each word is wrapped in a span and
   * animated in with staggered delays.
   *
   * @param {Object} options
   * @param {number} options.staggerMs   — Delay between each word (ms)
   * @param {number} options.threshold   — IntersectionObserver threshold
   */
  constructor({ staggerMs = 60, threshold = 0.2 } = {}) {
    this.staggerMs = staggerMs;

    this.observer = new IntersectionObserver(
      (entries) => this._handleIntersect(entries),
      { threshold }
    );

    this._prepare();
  }

  /** Wrap each word in a styled span, hide initially. */
  _prepare() {
    const elements = document.querySelectorAll('.text-reveal-words');

    elements.forEach((el) => {
      // Preserve the original text for screen-readers
      const text = el.textContent.trim();
      el.setAttribute('aria-label', text);

      const words = text.split(/\s+/);
      el.innerHTML = '';

      words.forEach((word, i) => {
        const span = document.createElement('span');
        span.innerHTML = word + '&nbsp;';
        span.style.cssText = `
          display: inline-block;
          opacity: 0;
          transform: translateY(14px);
          transition: opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1),
                      transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
          transition-delay: ${i * this.staggerMs}ms;
        `;
        el.appendChild(span);
      });

      this.observer.observe(el);
    });
  }

  _handleIntersect(entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const spans = entry.target.querySelectorAll('span');
        spans.forEach((span) => {
          span.style.opacity = '1';
          span.style.transform = 'translateY(0)';
        });
        this.observer.unobserve(entry.target);
      }
    });
  }

  destroy() {
    this.observer.disconnect();
  }
}


/* ── CounterAnimator ───────────────────────────────────────────────────────── */
class CounterAnimator {
  /**
   * Animates numeric counters from 0 to `data-target`.
   * Supports comma formatting and optional `+` suffix.
   *
   * @param {Object} options
   * @param {number} options.duration  — Animation duration in ms
   * @param {number} options.threshold — IntersectionObserver threshold
   */
  constructor({ duration = 2000, threshold = 0.3 } = {}) {
    this.duration = duration;

    this.observer = new IntersectionObserver(
      (entries) => this._handleIntersect(entries),
      { threshold }
    );

    this._observe();
  }

  _observe() {
    document.querySelectorAll('.counter').forEach((el) => {
      el.textContent = '0';
      this.observer.observe(el);
    });
  }

  _handleIntersect(entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        this._animate(entry.target);
        this.observer.unobserve(entry.target);
      }
    });
  }

  /**
   * Animate a single counter element.
   * @param {HTMLElement} el
   */
  _animate(el) {
    const target = parseInt(el.dataset.target, 10) || 0;
    const suffix = el.dataset.suffix || '';
    const useCommas = el.dataset.commas !== 'false';
    const start = performance.now();
    const duration = this.duration;

    const step = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);

      // Ease-out quint for natural deceleration
      const eased = 1 - Math.pow(1 - progress, 5);

      const current = Math.round(eased * target);
      el.textContent = (useCommas ? current.toLocaleString() : current) + suffix;

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    };

    requestAnimationFrame(step);
  }

  destroy() {
    this.observer.disconnect();
  }
}


/* ── ParallaxEngine ────────────────────────────────────────────────────────── */
class ParallaxEngine {
  /**
   * Applies subtle scroll-driven translateY to `.parallax` elements.
   * Speed is controlled by `data-speed` (default 0.15).
   *
   * Skips on devices that prefer reduced motion.
   */
  constructor() {
    // Bail out for reduced-motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    this.elements = [];
    this._gatherElements();

    this._ticking = false;
    this._onScroll = this._onScroll.bind(this);
    window.addEventListener('scroll', this._onScroll, { passive: true });

    // Initial calc
    this._update();
  }

  _gatherElements() {
    document.querySelectorAll('.parallax, .parallax-slow, .parallax-fast').forEach((el) => {
      let speed = parseFloat(el.dataset.speed);
      if (isNaN(speed)) {
        if (el.classList.contains('parallax-fast')) speed = 0.3;
        else if (el.classList.contains('parallax-slow')) speed = 0.08;
        else speed = 0.15;
      }
      this.elements.push({ el, speed });
    });
  }

  _onScroll() {
    if (!this._ticking) {
      requestAnimationFrame(() => {
        this._update();
        this._ticking = false;
      });
      this._ticking = true;
    }
  }

  _update() {
    const scrollY = window.scrollY;

    this.elements.forEach(({ el, speed }) => {
      const rect = el.getBoundingClientRect();
      const center = rect.top + rect.height / 2;
      const viewCenter = window.innerHeight / 2;
      const offset = (center - viewCenter) * speed;
      el.style.transform = `translateY(${offset}px)`;
    });
  }

  destroy() {
    window.removeEventListener('scroll', this._onScroll);
    this.elements.forEach(({ el }) => {
      el.style.transform = '';
    });
  }
}


/* ── MagneticButton ────────────────────────────────────────────────────────── */
class MagneticButton {
  /**
   * Creates a magnetic hover effect for elements with `.magnetic-btn`.
   * The button shifts toward the cursor on hover and snaps back on leave.
   *
   * @param {Object} options
   * @param {number} options.strength — Max pixel displacement (default 12)
   */
  constructor({ strength = 12 } = {}) {
    // Bail on touch-only devices
    if ('ontouchstart' in window && !window.matchMedia('(pointer: fine)').matches) return;

    this.strength = strength;
    this.buttons = document.querySelectorAll('.magnetic-btn');
    this._handlers = new Map();

    this.buttons.forEach((btn) => this._bind(btn));
  }

  _bind(btn) {
    const onMove = (e) => {
      const rect = btn.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;

      const dx = e.clientX - cx;
      const dy = e.clientY - cy;

      const maxDist = Math.max(rect.width, rect.height);
      const dist = Math.sqrt(dx * dx + dy * dy);
      const factor = Math.min(dist / maxDist, 1);

      const moveX = (dx / maxDist) * this.strength * factor;
      const moveY = (dy / maxDist) * this.strength * factor;

      btn.style.transform = `translate(${moveX}px, ${moveY}px)`;
    };

    const onLeave = () => {
      btn.style.transform = 'translate(0, 0)';
    };

    btn.addEventListener('mousemove', onMove);
    btn.addEventListener('mouseleave', onLeave);

    this._handlers.set(btn, { onMove, onLeave });
  }

  destroy() {
    this._handlers.forEach(({ onMove, onLeave }, btn) => {
      btn.removeEventListener('mousemove', onMove);
      btn.removeEventListener('mouseleave', onLeave);
      btn.style.transform = '';
    });
    this._handlers.clear();
  }
}


/* ── NavbarScrollEffect ────────────────────────────────────────────────────── */
class NavbarScrollEffect {
  /**
   * Toggles `.scrolled` on the `.navbar` element based on scroll position.
   *
   * @param {Object} options
   * @param {number} options.scrollThreshold — Pixels scrolled before toggle
   */
  constructor({ scrollThreshold = 100 } = {}) {
    this.navbar = document.querySelector('.navbar');
    if (!this.navbar) return;

    this.scrollThreshold = scrollThreshold;
    this._ticking = false;

    this._onScroll = this._onScroll.bind(this);
    window.addEventListener('scroll', this._onScroll, { passive: true });

    // Initial check
    this._update();
  }

  _onScroll() {
    if (!this._ticking) {
      requestAnimationFrame(() => {
        this._update();
        this._ticking = false;
      });
      this._ticking = true;
    }
  }

  _update() {
    if (window.scrollY > this.scrollThreshold) {
      this.navbar.classList.add('scrolled');
    } else {
      this.navbar.classList.remove('scrolled');
    }
  }

  destroy() {
    window.removeEventListener('scroll', this._onScroll);
    if (this.navbar) this.navbar.classList.remove('scrolled');
  }
}

/* ── CardHoverEffect ───────────────────────────────────────────────────────── */
class CardHoverEffect {
  constructor() {
    this.handleMouseMove = this.handleMouseMove.bind(this);
    // Use requestAnimationFrame for smooth performance
    this.ticking = false;
    this.clientX = 0;
    this.clientY = 0;
    
    document.addEventListener('mousemove', this.handleMouseMove);
  }
  
  handleMouseMove(e) {
    this.clientX = e.clientX;
    this.clientY = e.clientY;
    
    if (!this.ticking) {
      requestAnimationFrame(() => {
        this.updateCards();
        this.ticking = false;
      });
      this.ticking = true;
    }
  }
  
  updateCards() {
    const cards = document.querySelectorAll('.problem-card, .problem-card-featured');
    for (const card of cards) {
      const rect = card.getBoundingClientRect();
      const x = this.clientX - rect.left;
      const y = this.clientY - rect.top;
      
      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
      
      // Calculate 3D tilt
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      // Map mouse position to a subtle degree tilt (max 4deg)
      const rotateX = ((y - centerY) / centerY) * -4; 
      const rotateY = ((x - centerX) / centerX) * 4;
      
      // If mouse is inside the card
      if (x > 0 && x < rect.width && y > 0 && y < rect.height) {
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`;
      } else {
        card.style.transform = '';
      }
    }
  }

  destroy() {
    document.removeEventListener('mousemove', this.handleMouseMove);
  }
}


/* ── Init ──────────────────────────────────────────────────────────────────── */

/**
 * Boot every animation system. Call on DOMContentLoaded.
 * Returns a map of instances for later teardown if needed.
 */
function initAllAnimations() {
  const scrollAnimator    = new ScrollAnimator();
  const textRevealer      = new TextRevealer();
  const counterAnimator   = new CounterAnimator();
  const parallaxEngine    = new ParallaxEngine();
  const magneticButton    = new MagneticButton();
  const navbarScrollEffect = new NavbarScrollEffect();
  const cardHoverEffect   = new CardHoverEffect();

  // Expose for debugging / external control
  return {
    scrollAnimator,
    textRevealer,
    counterAnimator,
    parallaxEngine,
    magneticButton,
    navbarScrollEffect,
    cardHoverEffect,
  };
}

// Auto-init
document.addEventListener('DOMContentLoaded', () => {
  window.__fmiAnimations = initAllAnimations();
});
