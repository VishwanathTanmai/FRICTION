/**
 * Fix My Itch Clone — Main Application Logic
 * Handles API calls, problem loading, search, filtering, and form submission.
 */

// ─────────────────────────────────────────────
// Global State
// ─────────────────────────────────────────────
const AppState = {
    currentPage: 1,
    currentCategory: 'All',
    currentSort: 'overall_score',
    isLoading: false,
    hasMore: true,
    searchTimeout: null,
    analyzeTimeout: null,
    scratchCardInstance: null,
};

// ─────────────────────────────────────────────
// Theme Manager
// ─────────────────────────────────────────────
const ThemeManager = {
    init() {
        this.btn = document.getElementById('themeToggleBtn');
        this.icon = this.btn ? this.btn.querySelector('i') : null;
        
        if (this.btn) {
            this.btn.addEventListener('click', () => this.toggleTheme());
        }
        
        this.updateIcon();
    },
    
    toggleTheme() {
        document.documentElement.classList.toggle('dark-theme');
        const isDark = document.documentElement.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        this.updateIcon();
    },
    
    updateIcon() {
        if (!this.icon) return;
        if (document.documentElement.classList.contains('dark-theme')) {
            this.icon.className = 'bi bi-sun';
        } else {
            this.icon.className = 'bi bi-moon-stars';
        }
    }
};

// ─────────────────────────────────────────────
// API Helpers
// ─────────────────────────────────────────────
async function apiGet(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
}

async function apiPost(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
}

// ─────────────────────────────────────────────
// Score Color Helper
// ─────────────────────────────────────────────
function getScoreColor(score) {
    if (score >= 75) return '#10B981';
    if (score >= 50) return '#F59E0B';
    if (score >= 25) return '#F97316';
    return '#EF4444';
}

function getScoreGradient(score) {
    if (score >= 75) return 'linear-gradient(90deg, #10B981, #34D399)';
    if (score >= 50) return 'linear-gradient(90deg, #F59E0B, #FBBF24)';
    if (score >= 25) return 'linear-gradient(90deg, #F97316, #FB923C)';
    return 'linear-gradient(90deg, #EF4444, #F87171)';
}

// ─────────────────────────────────────────────
// Problem Card Renderer
// ─────────────────────────────────────────────
function renderProblemCard(problem) {
    const keywords = Array.isArray(problem.keyword_tags)
        ? problem.keyword_tags
        : (() => { try { return JSON.parse(problem.keyword_tags || '[]'); } catch { return []; } })();

    const keywordHtml = keywords.slice(0, 4).map(k => {
        const kw = typeof k === 'string' ? k : (k[0] || k);
        return `<span class="tag">${kw}</span>`;
    }).join('');

    return `
    <div class="col-lg-4 col-md-6">
        <div class="problem-card fade-up" data-id="${problem.id}">
            <div class="problem-card__header">
                <span class="tag tag-category">${problem.category}</span>
                <span class="problem-score-badge" style="background: ${getScoreGradient(problem.overall_score)}">
                    ${Math.round(problem.overall_score)}
                </span>
            </div>

            <h3 class="problem-card__title">${problem.title}</h3>

            ${problem.description ? `<p class="problem-card__description">${problem.description.substring(0, 120)}${problem.description.length > 120 ? '...' : ''}</p>` : ''}

            <div class="problem-card-scores">
                <div class="score-meter-inline">
                    <div class="score-meter">
                        <div class="score-meter__fill" style="width: ${problem.overall_score}%; background: ${getScoreGradient(problem.overall_score)}" data-score="${problem.overall_score}"></div>
                    </div>
                    <div class="score-meter__number">${Math.round(problem.overall_score)}</div>
                </div>
            </div>

            ${problem.root_cause ? `
            <div class="problem-card__meta">
                <div class="root-cause-tag">
                    <i class="bi bi-bullseye"></i>
                    <span>${problem.root_cause.substring(0, 60)}${problem.root_cause.length > 60 ? '...' : ''}</span>
                </div>
            </div>` : ''}

            <div class="problem-card-tags" style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;">${keywordHtml}</div>

            <div class="problem-card__footer">
                <div class="problem-scores-mini">
                    <span title="Frustration"><i class="bi bi-fire"></i> ${Math.round(problem.frustration_score)}</span>
                    <span title="Market Size"><i class="bi bi-graph-up"></i> ${Math.round(problem.market_size_score)}</span>
                    <span title="Solvability"><i class="bi bi-tools"></i> ${Math.round(problem.solvability_score)}</span>
                </div>
                <button class="btn-upvote" onclick="upvoteProblem(${problem.id}, this)" title="Upvote this problem">
                    <i class="bi bi-arrow-up-circle"></i>
                    <span>${problem.upvotes || 0}</span>
                </button>
            </div>
        </div>
    </div>`;
}

// ─────────────────────────────────────────────
// Load Problems
// ─────────────────────────────────────────────
async function loadProblems(reset = false) {
    if (AppState.isLoading) return;
    AppState.isLoading = true;

    const grid = document.getElementById('problemsGrid');
    const loading = document.getElementById('problemsLoading');
    const loadMore = document.getElementById('loadMoreContainer');
    const empty = document.getElementById('emptyState');

    if (reset) {
        AppState.currentPage = 1;
        AppState.hasMore = true;
        grid.innerHTML = '';
    }

    loading.style.display = 'block';
    loadMore.style.display = 'none';
    empty.style.display = 'none';

    const searchVal = document.getElementById('searchInput')?.value?.trim() || '';

    try {
        const params = new URLSearchParams({
            category: AppState.currentCategory,
            sort: AppState.currentSort,
            page: AppState.currentPage,
            per_page: 12,
        });
        if (searchVal) params.set('search', searchVal);

        const data = await apiGet(`/api/problems?${params}`);

        loading.style.display = 'none';

        if (data.problems.length === 0 && AppState.currentPage === 1) {
            empty.style.display = 'flex';
            return;
        }

        const html = data.problems.map(renderProblemCard).join('');
        grid.insertAdjacentHTML('beforeend', html);

        AppState.hasMore = data.has_next;
        if (AppState.hasMore) {
            loadMore.style.display = 'block';
        }

        // Re-init scroll animations for new cards
        if (typeof initAllAnimations === 'function') {
            setTimeout(() => initAllAnimations(), 100);
        }

    } catch (err) {
        console.error('Failed to load problems:', err);
        loading.style.display = 'none';
    } finally {
        AppState.isLoading = false;
    }
}

function loadMoreProblems() {
    AppState.currentPage++;
    loadProblems(false);
}

// ─────────────────────────────────────────────
// Category Filter
// ─────────────────────────────────────────────
function filterByCategory(category, btn) {
    AppState.currentCategory = category;

    // Update active state
    document.querySelectorAll('.category-filter-btn').forEach(p => p.classList.remove('active'));
    if (btn) btn.classList.add('active');

    loadProblems(true);
}

// ─────────────────────────────────────────────
// Sort
// ─────────────────────────────────────────────
function sortProblems(sortBy, btn) {
    AppState.currentSort = sortBy;

    document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');

    loadProblems(true);
}

// ─────────────────────────────────────────────
// Search
// ─────────────────────────────────────────────
function initSearch() {
    const input = document.getElementById('searchInput');
    if (!input) return;

    input.addEventListener('input', (e) => {
        clearTimeout(AppState.searchTimeout);
        const val = e.target.value.trim();

        const analyzing = document.getElementById('searchAnalyzing');
        const preview = document.getElementById('searchNlpPreview');

        if (val.length < 3) {
            preview.style.display = 'none';
            AppState.searchTimeout = setTimeout(() => loadProblems(true), 300);
            return;
        }

        analyzing.style.display = 'flex';

        AppState.searchTimeout = setTimeout(async () => {
            loadProblems(true);

            // Also run NLP analysis on search query
            if (val.length > 10) {
                try {
                    const analysis = await apiPost('/api/analyze', { text: val });
                    analyzing.style.display = 'none';
                    preview.style.display = 'flex';
                    document.getElementById('searchNlpScore').textContent =
                        `Score: ${Math.round(analysis.overall_score)} | Frustration: ${Math.round(analysis.frustration_score)}`;
                } catch {
                    analyzing.style.display = 'none';
                }
            } else {
                analyzing.style.display = 'none';
            }
        }, 500);
    });
}

// ─────────────────────────────────────────────
// Upvote
// ─────────────────────────────────────────────
async function upvoteProblem(id, btn) {
    try {
        btn.classList.add('upvoted');
        const data = await apiPost(`/api/upvote/${id}`, {});
        const countEl = btn.querySelector('span');
        if (countEl) countEl.textContent = data.upvotes;
    } catch (err) {
        console.error('Upvote failed:', err);
        btn.classList.remove('upvoted');
    }
}

// ─────────────────────────────────────────────
// Scratch Card Live & Buffer
// ─────────────────────────────────────────────
AppState.liveProblemsBuffer = [];

async function fetchLiveProblems() {
    const btn = document.getElementById('fetchLiveBtn');
    if (!btn) return;

    // Loading state
    const originalHtml = btn.innerHTML;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Scraping Live Web...`;
    btn.disabled = true;

    // Show loading in scratch card too
    const container = document.getElementById('scratchRevealContent');
    if (container) {
        container.innerHTML = `
            <div class="scratch-problem-loading text-center" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem; margin-bottom: 1rem;"></div>
                <h4 style="font-family: var(--font-display);">Analyzing Internet Data...</h4>
                <p class="text-muted" style="font-size: 0.875rem;">Scraping and running NLP processing...</p>
            </div>`;
    }

    try {
        const response = await apiGet('/api/scratch_live');
        if (response.problems && response.problems.length > 0) {
            AppState.liveProblemsBuffer = response.problems;
            loadNewScratchProblem(); // Load the first one from buffer
            
            // Show badge to indicate we're in live mode
            if (!document.getElementById('liveBadge')) {
                const badge = document.createElement('span');
                badge.id = 'liveBadge';
                badge.className = 'badge bg-success position-absolute top-0 end-0 m-3';
                badge.innerHTML = '<i class="bi bi-broadcast"></i> Live Data';
                const wrapper = document.getElementById('scratchCardContainer');
                if (wrapper) wrapper.appendChild(badge);
            }
        } else {
            alert('Could not fetch live problems at this time.');
            loadNewScratchProblem();
        }
    } catch (err) {
        console.error('Fetch live failed:', err);
        alert('Error fetching live problems.');
        loadNewScratchProblem();
    } finally {
        btn.innerHTML = originalHtml;
        btn.disabled = false;
    }
}

async function loadNewScratchProblem() {
    const container = document.getElementById('scratchRevealContent');
    if (!container) return;

    // Don't show loading if we already showed the scraping loading
    if (!container.innerHTML.includes('Analyzing Internet Data')) {
        container.innerHTML = `
            <div class="scratch-problem-loading">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <span>Loading a problem...</span>
            </div>`;
    }

        try {
            let problem;
            // Check buffer first
            if (AppState.liveProblemsBuffer.length > 0) {
                problem = AppState.liveProblemsBuffer.shift(); // take first
            } else {
                // Remove live badge if buffer empty
                const badge = document.getElementById('liveBadge');
                if (badge) badge.remove();
                
                const response = await apiGet('/api/scratch-reveal');
                if (response.problems && response.problems.length > 0) {
                    AppState.liveProblemsBuffer = response.problems;
                    problem = AppState.liveProblemsBuffer.shift();
                } else {
                    throw new Error('No problems returned');
                }
            }

            container.innerHTML = `
            <div class="scratch-revealed-problem">
                <span class="tag tag-category">${problem.category}</span>
                <h3 class="scratch-problem-title">${problem.title}</h3>
                <div class="scratch-score-display">
                    <div class="scratch-score-circle" style="--score-color: ${getScoreColor(problem.overall_score)}">
                        <span class="scratch-score-number">${Math.round(problem.overall_score)}</span>
                        <span class="scratch-score-label">Score</span>
                    </div>
                    <div class="scratch-score-details">
                        <div><i class="bi bi-fire"></i> Frustration: ${Math.round(problem.frustration_score)}</div>
                        <div><i class="bi bi-graph-up"></i> Market: ${Math.round(problem.market_size_score)}</div>
                        <div><i class="bi bi-tools"></i> Solvability: ${Math.round(problem.solvability_score)}</div>
                    </div>
                </div>
                ${problem.root_cause ? `<p class="scratch-root-cause"><i class="bi bi-bullseye"></i> ${problem.root_cause}</p>` : ''}
            </div>`;

        // Reinitialize scratch card canvas
        if (typeof ScratchCard !== 'undefined') {
            const canvas = document.getElementById('scratchCanvas');
            if (canvas) {
                AppState.scratchCardInstance = new ScratchCard('scratchCanvas', {
                    revealThreshold: 40,
                    brushSize: 45,
                    onReveal: () => {
                        document.querySelector('.scratch-instruction')?.classList.add('hidden');
                    }
                });
            }
        }

    } catch (err) {
        container.innerHTML = `
            <div class="scratch-problem-loading">
                <i class="bi bi-exclamation-circle text-danger"></i>
                <span>Failed to load. Try again.</span>
            </div>`;
        console.error('Scratch load failed:', err);
    }
}

// ─────────────────────────────────────────────
// Submit Form + Live Analysis
// ─────────────────────────────────────────────
function liveAnalyze(text) {
    clearTimeout(AppState.analyzeTimeout);
    const panel = document.getElementById('liveAnalysis');

    if (text.trim().length < 20) {
        panel.style.display = 'none';
        return;
    }

    AppState.analyzeTimeout = setTimeout(async () => {
        try {
            const category = document.getElementById('submitCategory')?.value || 'General';
            const analysis = await apiPost('/api/analyze', { text, category });

            panel.style.display = 'block';

            // Animate score bars
            animateScoreBar('liveFrustration', 'liveFrustrationVal', analysis.frustration_score);
            animateScoreBar('liveMarket', 'liveMarketVal', analysis.market_size_score);
            animateScoreBar('liveSolvability', 'liveSolvabilityVal', analysis.solvability_score);
            animateScoreBar('liveOverall', 'liveOverallVal', analysis.overall_score);

            // Root cause
            const rcEl = document.getElementById('liveRootCause');
            if (analysis.root_cause) {
                rcEl.style.display = 'block';
                document.getElementById('liveRootCauseText').textContent = analysis.root_cause;
            } else {
                rcEl.style.display = 'none';
            }

            // Keywords
            const kwEl = document.getElementById('liveKeywords');
            if (analysis.keywords && analysis.keywords.length > 0) {
                kwEl.style.display = 'block';
                const kwText = analysis.keywords.slice(0, 6).map(k =>
                    typeof k === 'string' ? k : k[0]
                ).join(', ');
                document.getElementById('liveKeywordsText').textContent = kwText;
            } else {
                kwEl.style.display = 'none';
            }

        } catch (err) {
            console.error('Live analysis failed:', err);
        }
    }, 600);
}

function animateScoreBar(barId, valId, score) {
    const bar = document.getElementById(barId);
    const val = document.getElementById(valId);
    if (!bar || !val) return;

    bar.style.width = `${Math.min(100, score)}%`;
    bar.style.background = getScoreGradient(score);
    val.textContent = Math.round(score);
}

async function submitProblem(event) {
    event.preventDefault();

    const text = document.getElementById('submitText').value.trim();
    const category = document.getElementById('submitCategory').value;
    const email = document.getElementById('submitEmail').value.trim();
    const btn = document.getElementById('submitBtn');

    if (text.length < 20) return;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';

    try {
        await apiPost('/api/submit', { text, category, email });

        document.getElementById('submitForm').style.display = 'none';
        document.getElementById('liveAnalysis').style.display = 'none';
        document.getElementById('submitSuccess').style.display = 'flex';

    } catch (err) {
        console.error('Submit failed:', err);
        btn.innerHTML = '<i class="bi bi-exclamation-circle me-2"></i>Failed — Try Again';
        btn.disabled = false;
    }
}

function resetSubmitForm() {
    document.getElementById('submitForm').style.display = 'block';
    document.getElementById('submitForm').reset();
    document.getElementById('submitSuccess').style.display = 'none';
    document.getElementById('liveAnalysis').style.display = 'none';
    const btn = document.getElementById('submitBtn');
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-send me-2"></i>Submit & Analyze';
}

// ─────────────────────────────────────────────
// Initialization
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Init Theme
    ThemeManager.init();

    // Load problems grid
    loadProblems(true);

    // Initialize search
    initSearch();

    // Load scratch card
    loadNewScratchProblem();

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
