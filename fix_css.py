import os

HTML_FILE = "templates/index.html"
JS_FILE = "static/js/app.js"

replacements = {
    # Hero
    'class="hero-noise"': 'class="noise-overlay"',
    'class="hero-gradient-orb hero-orb-1"': 'class="hero-float hero-float-1"',
    'class="hero-gradient-orb hero-orb-2"': 'class="hero-float hero-float-2"',
    'hero-container': 'hero-content',
    'hero-eyebrow': 'hero-subtitle text-uppercase',
    'hero-stats fade-up stagger-4"': 'stats-grid fade-up stagger-4" style="margin-top: 3rem;"',
    'class="hero-stat"': 'class="stat-item"',
    'class="hero-stat-number counter"': 'class="stat-item__number counter"',
    'class="hero-stat-number gradient-text"': 'class="stat-item__number gradient-text"',
    'class="hero-stat-number"': 'class="stat-item__number"',
    'class="hero-stat-label"': 'class="stat-item__label"',
    '<div class="hero-stat-divider"></div>': '',

    # Cards
    'problem-card-header': 'problem-card__header',
    'problem-card-title': 'problem-card__title',
    'problem-card-desc': 'problem-card__description',
    'problem-card-meta': 'problem-card__meta',
    'problem-card-footer': 'problem-card__footer',
    '<div class="score-meter">': '<div class="score-meter-inline"><div class="score-meter">',
    '</div>\n                            </div>\n                        </div>': '</div>\n                            </div>\n                        </div></div>',
    'score-meter-label': 'visually-hidden',
    'class="score-value"': 'class="score-meter__value"',
    'score-meter-bar': 'score-meter',
    'score-meter-fill': 'score-meter__fill',
    
    # Search
    'search-input': 'search-bar__input',
    'search-icon': 'search-bar__icon',

    # Filters
    'filter-pill': 'category-filter-btn',

    # Stats section
    'stat-number': 'stat-item__number',
    'stat-label': 'stat-item__label',

    # Form
    'submit-card': 'submit-form',
    'form-floating-custom': 'form-float',
    'submit-textarea': 'form-float__textarea',
    'submit-select': 'form-float__input',
    'submit-input': 'form-float__input',
    'live-analysis"': 'form-live-preview"',
    '<label for="submitText"': '<label class="form-float__label" for="submitText"',

    # Footer
    'site-footer': 'footer',
    'footer-brand': 'footer__brand',
    'footer-tagline': 'footer__tagline',
    'footer-note': 'footer__bottom',
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix score meter HTML structure for inline display
    content = content.replace(
        '<div class="score-meter">\n                            <div class="score-meter-label">\n                                <span>Overall Score</span>\n                                <span class="score-value">{{ "%.0f"|format(problem.overall_score) }}</span>\n                            </div>\n                            <div class="score-meter-bar">\n                                <div class="score-meter-fill" style="width: {{ problem.overall_score }}%"\n                                     data-score="{{ problem.overall_score }}"></div>\n                            </div>\n                        </div>',
        '<div class="score-meter-inline">\n                            <div class="score-meter">\n                                <div class="score-meter__fill" style="width: {{ problem.overall_score }}%"></div>\n                            </div>\n                            <div class="score-meter__number">{{ "%.0f"|format(problem.overall_score) }}</div>\n                        </div>'
    )

    for old, new in replacements.items():
        content = content.replace(old, new)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")

fix_file(HTML_FILE)
fix_file(JS_FILE)
