"""
Web Scraper Module for Fix My Itch Clone.
Scrapes problem statements from various web sources.
Uses requests + BeautifulSoup (no external APIs).

NOTE: Web scraping may be blocked by target sites.
The app works standalone with seed data — this module is optional.
"""

import re
import time
import json
import hashlib
import sqlite3
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    print("[SCRAPER] requests/bs4 not installed. Run: pip install requests beautifulsoup4")


class ProblemScraper:
    """Scrapes and deduplicates problem statements from web sources."""

    # Rate limiting
    REQUEST_DELAY = 2.0  # seconds between requests

    # User agent to avoid blocks
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    # Category keywords for auto-classification
    CATEGORY_KEYWORDS = {
        'Health': ['health', 'medical', 'doctor', 'hospital', 'medicine', 'disease',
                   'mental health', 'anxiety', 'depression', 'sleep', 'fitness', 'diet',
                   'insurance', 'healthcare', 'patient', 'treatment', 'therapy', 'wellness'],
        'Finance': ['finance', 'money', 'bank', 'loan', 'credit', 'investment', 'tax',
                    'gst', 'payment', 'salary', 'savings', 'insurance', 'upi', 'fintech',
                    'debt', 'mutual fund', 'stock', 'budget', 'expense'],
        'Education': ['education', 'school', 'college', 'university', 'student', 'teacher',
                      'exam', 'tuition', 'course', 'learn', 'skill', 'training', 'test prep',
                      'coaching', 'scholarship', 'degree', 'online class'],
        'Logistics': ['delivery', 'shipping', 'logistics', 'courier', 'warehouse', 'supply chain',
                      'last mile', 'package', 'ecommerce', 'return', 'tracking'],
        'Food': ['food', 'restaurant', 'cooking', 'grocery', 'diet', 'nutrition', 'meal',
                 'kitchen', 'recipe', 'vegetarian', 'vegan', 'allergy', 'organic', 'delivery'],
        'Legal': ['legal', 'law', 'court', 'lawyer', 'contract', 'rights', 'tenant',
                  'landlord', 'consumer', 'complaint', 'regulation', 'compliance', 'dispute'],
        'Transport': ['transport', 'commute', 'traffic', 'bus', 'train', 'metro', 'auto',
                      'cab', 'uber', 'ola', 'parking', 'road', 'fuel', 'ev', 'electric vehicle'],
        'Housing': ['housing', 'rent', 'apartment', 'flat', 'property', 'broker', 'lease',
                    'co-living', 'pg', 'real estate', 'mortgage', 'construction', 'interior'],
        'Agriculture': ['agriculture', 'farming', 'crop', 'farmer', 'soil', 'irrigation',
                        'harvest', 'pesticide', 'market', 'mandi', 'middlemen', 'agritech'],
        'Environment': ['environment', 'pollution', 'waste', 'recycling', 'sustainable',
                        'climate', 'carbon', 'green', 'solar', 'water', 'air quality', 'plastic'],
        'Technology': ['technology', 'internet', 'software', 'app', 'digital', 'ai',
                       'cybersecurity', 'data', 'privacy', 'startup', 'saas', 'cloud'],
        'Employment': ['job', 'employment', 'hiring', 'resume', 'interview', 'career',
                       'freelance', 'gig', 'salary', 'layoff', 'workplace', 'remote work'],
    }

    def __init__(self):
        self.seen_hashes = set()

    def _text_hash(self, text):
        """Generate hash for deduplication."""
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()

    def _is_duplicate(self, text):
        """Check if text is a duplicate."""
        h = self._text_hash(text)
        if h in self.seen_hashes:
            return True
        self.seen_hashes.add(h)
        return False

    def _classify_category(self, text):
        """Auto-classify text into a category based on keyword matching."""
        text_lower = text.lower()
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score

        if scores:
            return max(scores, key=scores.get)
        return 'General'

    def _clean_text(self, text):
        """Clean scraped text."""
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
        text = text.strip()
        return text

    def _is_valid_problem(self, text):
        """Check if text is a valid problem statement."""
        if len(text) < 30:
            return False
        if len(text) > 500:
            return False
        # Should contain problem indicators
        problem_words = ['why', 'can\'t', 'cannot', 'struggle', 'difficult', 'hard',
                         'problem', 'issue', 'frustrat', 'challenge', 'need', 'want',
                         'lack', 'missing', 'broken', 'expensive', 'slow', 'complain']
        text_lower = text.lower()
        return any(w in text_lower for w in problem_words)

    def fetch_page(self, url):
        """Fetch a web page with error handling."""
        if not HAS_DEPS:
            print("[SCRAPER] Missing dependencies")
            return None
        try:
            time.sleep(self.REQUEST_DELAY)
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"[SCRAPER] Failed to fetch {url}: {e}")
            return None

    def scrape_generic_page(self, url, selectors=None):
        """Scrape problem-like text from any page."""
        soup = self.fetch_page(url)
        if not soup:
            return []

        problems = []
        # Try common text selectors
        if selectors is None:
            selectors = ['p', 'h2', 'h3', 'li', '.post-title', '.comment-body',
                         'article p', '.content p', '.titleline a']

        for selector in selectors:
            elements = soup.select(selector)
            for el in elements:
                text = self._clean_text(el.get_text())
                if self._is_valid_problem(text) and not self._is_duplicate(text):
                    category = self._classify_category(text)
                    problems.append({
                        'title': text,
                        'description': '',
                        'category': category,
                        'source': url,
                        'source_url': url,
                    })

        return problems

    def scrape_and_process(self, urls, nlp_engine=None):
        """
        Scrape multiple URLs and optionally process through NLP.

        Args:
            urls: List of URLs to scrape
            nlp_engine: Optional NLPEngine instance for scoring

        Returns:
            List of problem dicts with scores
        """
        all_problems = []

        for url in urls:
            print(f"[SCRAPER] Scraping: {url}")
            problems = self.scrape_generic_page(url)
            print(f"[SCRAPER] Found {len(problems)} problems")
            all_problems.extend(problems)

        # Process through NLP if available
        if nlp_engine and all_problems:
            print(f"[SCRAPER] Processing {len(all_problems)} problems through NLP...")
            for p in all_problems:
                try:
                    analysis = nlp_engine.analyze_problem(p['title'], p['category'])
                    p.update({
                        'frustration_score': analysis.get('frustration_score', 0),
                        'market_size_score': analysis.get('market_size_score', 0),
                        'solvability_score': analysis.get('solvability_score', 0),
                        'overall_score': analysis.get('overall_score', 0),
                        'root_cause': analysis.get('root_cause', ''),
                        'inefficiency': json.dumps(analysis.get('inefficiencies', [])),
                        'sentiment': analysis.get('sentiment', 0),
                        'keyword_tags': analysis.get('keywords', []),
                    })
                except Exception as e:
                    print(f"[SCRAPER] NLP error: {e}")

        return all_problems


def scrape_to_database(urls, db_path, nlp_engine=None):
    """Convenience function to scrape URLs and insert into database."""
    from models import get_db, insert_problem

    scraper = ProblemScraper()
    problems = scraper.scrape_and_process(urls, nlp_engine)

    if not problems:
        print("[SCRAPER] No problems found")
        return 0

    conn = get_db(db_path)
    count = 0
    for p in problems:
        try:
            insert_problem(conn, p)
            count += 1
        except Exception as e:
            print(f"[SCRAPER] Insert error: {e}")

    conn.commit()
    conn.close()
    print(f"[SCRAPER] Inserted {count} problems into database")
    return count


if __name__ == '__main__':
    # Example usage
    print("Web Scraper Module")
    print("=" * 40)
    print("This module provides scraping utilities.")
    print("Import and use ProblemScraper or scrape_to_database().")
    print("\nExample:")
    print("  from scraper import scrape_to_database")
    print("  from nlp_engine import NLPEngine")
    print("  nlp = NLPEngine()")
    print("  scrape_to_database(['https://example.com'], 'fixmyitch.db', nlp)")
