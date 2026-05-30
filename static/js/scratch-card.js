/* ═══════════════════════════════════════════════════════════════════════════════
   FIX MY ITCH — Scratch Card Component
   Canvas scratch-to-reveal · Particle FX · Touch & Mouse · Auto-reveal
   ═══════════════════════════════════════════════════════════════════════════════ */

'use strict';

/* ── Particle (internal) ───────────────────────────────────────────────────── */
class _ScratchParticle {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.size = Math.random() * 3 + 1.5;
    this.speedX = (Math.random() - 0.5) * 4;
    this.speedY = (Math.random() - 0.5) * 4 - 1; // slight upward bias
    this.alpha = 1;
    this.decay = Math.random() * 0.03 + 0.02;
    this.color = `hsl(${220 + Math.random() * 60}, 70%, 65%)`;
  }

  update() {
    this.x += this.speedX;
    this.y += this.speedY;
    this.alpha -= this.decay;
    this.size *= 0.97;
  }

  draw(ctx) {
    if (this.alpha <= 0) return;
    ctx.save();
    ctx.globalAlpha = this.alpha;
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  get isDead() {
    return this.alpha <= 0;
  }
}


/* ── ScratchCard ───────────────────────────────────────────────────────────── */
class ScratchCard {
  /**
   * @param {Object} config
   * @param {string}   config.canvasId         — ID of the <canvas> element
   * @param {string}   config.revealContentId  — ID of the hidden content element
   * @param {string}   [config.coverColor]     — Cover color/gradient (CSS)
   * @param {number}   [config.brushSize=40]   — Eraser brush radius
   * @param {number}   [config.revealThreshold=40] — % scratched to auto-reveal
   * @param {Function} [config.onReveal]       — Callback when fully revealed
   */
  constructor({
    canvasId,
    revealContentId,
    coverColor,
    brushSize = 40,
    revealThreshold = 40,
    onReveal,
  }) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) {
      console.warn(`[ScratchCard] Canvas #${canvasId} not found.`);
      return;
    }

    this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });
    this.revealEl = document.getElementById(revealContentId);
    this.coverColor = coverColor || null;
    this.brushSize = brushSize;
    this.revealThreshold = revealThreshold;
    this.onReveal = onReveal || (() => {});

    this.isDrawing = false;
    this.isRevealed = false;
    this.particles = [];
    this._animFrameId = null;
    this._checkInterval = null;
    this._instructionEl = null;
    this._scratchStarted = false;

    this._init();
  }

  /* ─── Setup ──────────────────────────────────────────────────────────────── */

  _init() {
    this._resize();
    this._drawCover();
    this._bindEvents();
    this._startParticleLoop();

    // Find sibling instruction element
    this._instructionEl = this.canvas.parentElement?.querySelector('.scratch-instruction');
  }

  _resize() {
    const parent = this.canvas.parentElement;
    const rect = parent.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;

    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.canvas.style.width = rect.width + 'px';
    this.canvas.style.height = rect.height + 'px';

    this.ctx.scale(dpr, dpr);
    this._width = rect.width;
    this._height = rect.height;
  }

  _drawCover() {
    const ctx = this.ctx;

    if (this.coverColor) {
      ctx.fillStyle = this.coverColor;
      ctx.fillRect(0, 0, this._width, this._height);
    } else {
      // Premium dark gradient
      const grad = ctx.createLinearGradient(0, 0, this._width, this._height);
      grad.addColorStop(0, '#1a1a2e');
      grad.addColorStop(0.5, '#16213e');
      grad.addColorStop(1, '#0f3460');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, this._width, this._height);

      // Subtle pattern overlay
      this._drawNoisePattern();
    }
  }

  /** Draw a subtle stipple/noise pattern over the cover. */
  _drawNoisePattern() {
    const ctx = this.ctx;
    const w = this._width;
    const h = this._height;

    ctx.save();
    ctx.globalAlpha = 0.08;
    for (let i = 0; i < 4000; i++) {
      const x = Math.random() * w;
      const y = Math.random() * h;
      const r = Math.random() * 1.2;
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  /* ─── Events ─────────────────────────────────────────────────────────────── */

  _bindEvents() {
    // Mouse
    this.canvas.addEventListener('mousedown', (e) => this._startDraw(e));
    this.canvas.addEventListener('mousemove', (e) => this._draw(e));
    this.canvas.addEventListener('mouseup', () => this._stopDraw());
    this.canvas.addEventListener('mouseleave', () => this._stopDraw());

    // Touch
    this.canvas.addEventListener('touchstart', (e) => this._startDraw(e), { passive: false });
    this.canvas.addEventListener('touchmove', (e) => this._draw(e), { passive: false });
    this.canvas.addEventListener('touchend', () => this._stopDraw());
    this.canvas.addEventListener('touchcancel', () => this._stopDraw());

    // Resize
    this._resizeHandler = () => {
      if (!this.isRevealed) {
        this._resize();
        this._drawCover();
      }
    };
    window.addEventListener('resize', this._resizeHandler);
  }

  _getPos(e) {
    const rect = this.canvas.getBoundingClientRect();
    let clientX, clientY;

    if (e.touches && e.touches.length > 0) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = e.clientX;
      clientY = e.clientY;
    }

    return {
      x: clientX - rect.left,
      y: clientY - rect.top,
    };
  }

  _startDraw(e) {
    if (this.isRevealed) return;
    e.preventDefault();
    this.isDrawing = true;

    if (!this._scratchStarted) {
      this._scratchStarted = true;
      if (this._instructionEl) {
        this._instructionEl.classList.add('hidden');
      }
      // Start periodic percentage checks
      this._checkInterval = setInterval(() => this._checkReveal(), 300);
    }

    const pos = this._getPos(e);
    this._lastPos = pos;
    this._scratch(pos.x, pos.y);
  }

  _draw(e) {
    if (!this.isDrawing || this.isRevealed) return;
    e.preventDefault();

    const pos = this._getPos(e);

    // Interpolate between last pos and current for smooth strokes
    if (this._lastPos) {
      const dx = pos.x - this._lastPos.x;
      const dy = pos.y - this._lastPos.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const steps = Math.max(Math.floor(dist / (this.brushSize * 0.3)), 1);

      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        const ix = this._lastPos.x + dx * t;
        const iy = this._lastPos.y + dy * t;
        this._scratch(ix, iy);
      }
    }

    // Emit particles
    this._emitParticles(pos.x, pos.y, 2);

    this._lastPos = pos;
  }

  _stopDraw() {
    this.isDrawing = false;
    this._lastPos = null;
  }

  _scratch(x, y) {
    const ctx = this.ctx;
    ctx.save();
    ctx.globalCompositeOperation = 'destination-out';
    ctx.beginPath();
    ctx.arc(x, y, this.brushSize / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  /* ─── Percentage & Reveal ────────────────────────────────────────────────── */

  _getScratchedPercent() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    const data = ctx.getImageData(0, 0, w, h).data;

    let transparent = 0;
    const total = w * h;

    // Sample every 4th pixel for performance
    for (let i = 3; i < data.length; i += 16) {
      if (data[i] === 0) transparent++;
    }

    return (transparent / (total / 4)) * 100;
  }

  _checkReveal() {
    if (this.isRevealed) return;

    const pct = this._getScratchedPercent();
    if (pct >= this.revealThreshold) {
      this._reveal();
    }
  }

  _reveal() {
    if (this.isRevealed) return;
    this.isRevealed = true;

    clearInterval(this._checkInterval);

    // Animate canvas fade out
    this.canvas.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
    this.canvas.style.opacity = '0';

    // Show reveal content
    if (this.revealEl) {
      this.revealEl.style.opacity = '1';
      this.revealEl.style.transform = 'scale(1)';
    }

    setTimeout(() => {
      this.canvas.style.pointerEvents = 'none';
      this.onReveal();
    }, 600);
  }

  /* ─── Particles ──────────────────────────────────────────────────────────── */

  _emitParticles(x, y, count) {
    for (let i = 0; i < count; i++) {
      this.particles.push(new _ScratchParticle(x, y));
    }
  }

  _startParticleLoop() {
    // We draw particles on a separate pass using source-over
    const loop = () => {
      this._animFrameId = requestAnimationFrame(loop);

      if (this.particles.length === 0 || this.isRevealed) return;

      const ctx = this.ctx;
      ctx.save();
      ctx.globalCompositeOperation = 'source-over';

      this.particles.forEach((p) => {
        p.update();
        p.draw(ctx);
      });

      // Remove dead particles
      this.particles = this.particles.filter((p) => !p.isDead);

      ctx.restore();
    };

    this._animFrameId = requestAnimationFrame(loop);
  }

  /* ─── Public API ─────────────────────────────────────────────────────────── */

  /** Re-cover the card for reuse with a new problem. */
  reset() {
    this.isRevealed = false;
    this.isDrawing = false;
    this._scratchStarted = false;
    this._lastPos = null;
    this.particles = [];

    clearInterval(this._checkInterval);

    this.canvas.style.transition = 'none';
    this.canvas.style.opacity = '1';
    this.canvas.style.pointerEvents = 'auto';

    if (this._instructionEl) {
      this._instructionEl.classList.remove('hidden');
    }

    if (this.revealEl) {
      this.revealEl.style.opacity = '0';
      this.revealEl.style.transform = 'scale(0.95)';
    }

    this._resize();
    this._drawCover();
  }

  /** Clean up all listeners and animation frames. */
  destroy() {
    clearInterval(this._checkInterval);
    cancelAnimationFrame(this._animFrameId);
    window.removeEventListener('resize', this._resizeHandler);
  }
}


/* ── createScratchCard helper ──────────────────────────────────────────────── */

/**
 * Factory function that builds the DOM, styles, and initialises a ScratchCard.
 *
 * @param {string} containerId — ID of an existing empty container element
 * @param {Object} problemData
 * @param {string} problemData.title    — Problem headline
 * @param {string} problemData.category — e.g. "UX", "Performance"
 * @param {number} problemData.score    — 0-100 itch score
 * @param {string} [problemData.description] — Optional short description
 * @param {Function} [onReveal] — Callback when revealed
 * @returns {ScratchCard|null}
 */
function createScratchCard(containerId, problemData, onReveal) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.warn(`[createScratchCard] Container #${containerId} not found.`);
    return null;
  }

  // Unique IDs
  const uid = `sc_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
  const canvasId = `${uid}_canvas`;
  const revealId = `${uid}_reveal`;

  // Determine score colour tier
  const score = Math.max(0, Math.min(100, problemData.score || 0));
  let scoreColor = '#EF4444'; // danger
  let scoreTier = 'low';
  if (score >= 70) {
    scoreColor = '#10B981';
    scoreTier = 'high';
  } else if (score >= 40) {
    scoreColor = '#F59E0B';
    scoreTier = 'mid';
  }

  // Category → tag class mapping
  const catClass = {
    ux: 'tag-category--ux',
    performance: 'tag-category--performance',
    onboarding: 'tag-category--onboarding',
    pricing: 'tag-category--pricing',
    support: 'tag-category--support',
    feature: 'tag-category--feature',
    mobile: 'tag-category--mobile',
  };
  const catKey = (problemData.category || '').toLowerCase().replace(/\s+/g, '');
  const tagClass = catClass[catKey] || 'tag-category--ux';

  // Build HTML
  container.classList.add('scratch-card-wrapper');

  container.innerHTML = `
    <!-- Reveal content (hidden initially) -->
    <div class="scratch-card-reveal" id="${revealId}"
         style="opacity: 0; transform: scale(0.95); transition: opacity 0.6s cubic-bezier(0.16,1,0.3,1), transform 0.6s cubic-bezier(0.16,1,0.3,1);">
      <span class="tag tag-category ${tagClass}" style="margin-bottom: 0.75rem;">
        ${_escapeHtml(problemData.category || 'General')}
      </span>
      <h3 class="problem-title">${_escapeHtml(problemData.title)}</h3>
      ${problemData.description ? `<p class="text-body-sm" style="margin-bottom:1rem; max-width:320px;">${_escapeHtml(problemData.description)}</p>` : ''}
      <div class="score-meter-inline" style="width: 100%; max-width: 200px; margin-top: 0.75rem;">
        <div class="score-meter">
          <div class="score-meter__fill"
               data-score-${scoreTier}
               style="width: ${score}%; background: linear-gradient(90deg, #EF4444, #F59E0B, #10B981); background-size: 300% 100%; background-position: ${score}% 50%;"></div>
        </div>
        <span class="score-meter__number" style="color: ${scoreColor}; font-weight: 700;">${score}</span>
      </div>
    </div>

    <!-- Canvas overlay -->
    <canvas class="scratch-card-canvas" id="${canvasId}"></canvas>

    <!-- Instruction -->
    <span class="scratch-instruction">Scratch to reveal a problem worth solving</span>
  `;

  // Init
  const instance = new ScratchCard({
    canvasId,
    revealContentId: revealId,
    brushSize: 40,
    revealThreshold: 40,
    onReveal: onReveal || (() => {}),
  });

  return instance;
}


/* ── Utility ───────────────────────────────────────────────────────────────── */

function _escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
