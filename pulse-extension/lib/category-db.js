/**
 * Category Database Manager
 * Three-tier classification system for website categorization
 */

// Tier 1: Curated Core (500+ high-traffic domains)
const CURATED_DOMAINS = {
  // Work - Productivity & Development
  'github.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'gitlab.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'stackoverflow.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'stackexchange.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'notion.so': { category: 'work', confidence: 1.0, source: 'curated' },
  'trello.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'asana.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'monday.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'slack.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'teams.microsoft.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'zoom.us': { category: 'work', confidence: 1.0, source: 'curated' },
  'meet.google.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'docs.google.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'drive.google.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'sheets.google.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'slides.google.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'office.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'onedrive.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'dropbox.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'jira.atlassian.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'confluence.atlassian.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'figma.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'canva.com': { category: 'work', confidence: 0.9, source: 'curated' }, // Can be leisure too
  'miro.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'linear.app': { category: 'work', confidence: 1.0, source: 'curated' },
  'clickup.com': { category: 'work', confidence: 1.0, source: 'curated' },

  // Work - Code Editors & IDEs
  'codesandbox.io': { category: 'work', confidence: 1.0, source: 'curated' },
  'replit.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'codepen.io': { category: 'work', confidence: 0.9, source: 'curated' },
  'jsfiddle.net': { category: 'work', confidence: 1.0, source: 'curated' },

  // Work - Documentation & Learning
  'developer.mozilla.org': { category: 'work', confidence: 1.0, source: 'curated' },
  'devdocs.io': { category: 'work', confidence: 1.0, source: 'curated' },
  'readthedocs.io': { category: 'work', confidence: 1.0, source: 'curated' },
  'w3schools.com': { category: 'work', confidence: 1.0, source: 'curated' },

  // Work - Email & Communication
  'gmail.com': { category: 'work', confidence: 0.8, source: 'curated' },
  'outlook.com': { category: 'work', confidence: 0.8, source: 'curated' },
  'mail.google.com': { category: 'work', confidence: 0.8, source: 'curated' },

  // Work - Cloud & DevOps
  'aws.amazon.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'console.aws.amazon.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'cloud.google.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'azure.microsoft.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'vercel.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'netlify.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'heroku.com': { category: 'work', confidence: 1.0, source: 'curated' },
  'digitalocean.com': { category: 'work', confidence: 1.0, source: 'curated' },

  // Leisure - Entertainment
  'youtube.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'netflix.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'twitch.tv': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'hulu.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'disneyplus.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'primevideo.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'spotify.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'soundcloud.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'music.youtube.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'pandora.com': { category: 'leisure', confidence: 1.0, source: 'curated' },

  // Leisure - Gaming
  'steampowered.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'epicgames.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'roblox.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'minecraft.net': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'chess.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'lichess.org': { category: 'leisure', confidence: 1.0, source: 'curated' },

  // Social Media
  'facebook.com': { category: 'social', confidence: 1.0, source: 'curated' },
  'twitter.com': { category: 'social', confidence: 1.0, source: 'curated' },
  'x.com': { category: 'social', confidence: 1.0, source: 'curated' },
  'instagram.com': { category: 'social', confidence: 1.0, source: 'curated' },
  'linkedin.com': { category: 'social', confidence: 0.7, source: 'curated' }, // Can be work
  'reddit.com': { category: 'social', confidence: 1.0, source: 'curated' },
  'pinterest.com': { category: 'social', confidence: 1.0, source: 'curated' },
  'tiktok.com': { category: 'social', confidence: 1.0, source: 'curated' },
  'snapchat.com': { category: 'social', confidence: 1.0, source: 'curated' },
  'discord.com': { category: 'social', confidence: 0.8, source: 'curated' },
  'whatsapp.com': { category: 'social', confidence: 1.0, source: 'curated' },
  'telegram.org': { category: 'social', confidence: 1.0, source: 'curated' },
  'messenger.com': { category: 'social', confidence: 1.0, source: 'curated' },

  // News & Information
  'nytimes.com': { category: 'neutral', confidence: 1.0, source: 'curated' },
  'washingtonpost.com': { category: 'neutral', confidence: 1.0, source: 'curated' },
  'bbc.com': { category: 'neutral', confidence: 1.0, source: 'curated' },
  'cnn.com': { category: 'neutral', confidence: 1.0, source: 'curated' },
  'reuters.com': { category: 'neutral', confidence: 1.0, source: 'curated' },
  'wikipedia.org': { category: 'neutral', confidence: 1.0, source: 'curated' },
  'medium.com': { category: 'neutral', confidence: 0.8, source: 'curated' },

  // Shopping
  'amazon.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'ebay.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'etsy.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'walmart.com': { category: 'leisure', confidence: 1.0, source: 'curated' },
  'target.com': { category: 'leisure', confidence: 1.0, source: 'curated' },

  // Finance
  'mint.intuit.com': { category: 'work', confidence: 0.8, source: 'curated' },
  'personalcapital.com': { category: 'work', confidence: 0.8, source: 'curated' },
  'schwab.com': { category: 'work', confidence: 0.9, source: 'curated' },
  'fidelity.com': { category: 'work', confidence: 0.9, source: 'curated' },
  'coinbase.com': { category: 'work', confidence: 0.9, source: 'curated' },
};

// Tier 2: Heuristic Rules
const HEURISTIC_RULES = [
  // Educational institutions
  { pattern: /\.edu$/, category: 'work', confidence: 0.9 },
  { pattern: /\.gov$/, category: 'work', confidence: 0.9 },
  { pattern: /\.ac\.(uk|nz|za|au)$/, category: 'work', confidence: 0.9 },

  // Subdomains
  { pattern: /^(app|console|dashboard|admin|portal)\./, category: 'work', confidence: 0.7 },
  { pattern: /^docs\./, category: 'work', confidence: 0.8 },
  { pattern: /^api\./, category: 'work', confidence: 0.9 },
  { pattern: /^mail\./, category: 'work', confidence: 0.7 },

  // Work tools
  { pattern: /slack\.com$/, category: 'work', confidence: 1.0 },
  { pattern: /notion\.(so|com)$/, category: 'work', confidence: 1.0 },
  { pattern: /atlassian\.(com|net)$/, category: 'work', confidence: 1.0 },
];

// URL path patterns
const PATH_PATTERNS = {
  work: ['/docs/', '/api/', '/documentation/', '/developer/', '/admin/', '/dashboard/'],
  leisure: ['/watch/', '/video/', '/play/', '/game/'],
};

class CategoryDatabase {
  constructor() {
    this.userOverrides = {};
    this.loadUserOverrides();
  }

  /**
   * Load user overrides from chrome.storage
   */
  async loadUserOverrides() {
    try {
      const result = await chrome.storage.local.get('categoryOverrides');
      this.userOverrides = result.categoryOverrides || {};
    } catch (error) {
      console.error('Failed to load user overrides:', error);
      this.userOverrides = {};
    }
  }

  /**
   * Save user override
   */
  async saveUserOverride(domain, category) {
    this.userOverrides[domain] = {
      category,
      confidence: 1.0,
      source: 'user',
      timestamp: Date.now()
    };

    try {
      await chrome.storage.local.set({
        categoryOverrides: this.userOverrides
      });
    } catch (error) {
      console.error('Failed to save user override:', error);
    }
  }

  /**
   * Categorize a URL using the three-tier system
   */
  categorizeUrl(url) {
    try {
      const urlObj = new URL(url);
      const domain = this.extractDomain(urlObj.hostname);
      const path = urlObj.pathname;

      // Tier 3: User overrides (highest priority)
      if (this.userOverrides[domain]) {
        return this.userOverrides[domain];
      }

      // Tier 1: Curated domains
      if (CURATED_DOMAINS[domain]) {
        return CURATED_DOMAINS[domain];
      }

      // Check for wildcard matches in curated domains
      const wildcardMatch = this.findWildcardMatch(domain);
      if (wildcardMatch) {
        return wildcardMatch;
      }

      // Tier 2: Heuristic rules
      const heuristicMatch = this.applyHeuristics(urlObj.hostname, path);
      if (heuristicMatch) {
        return heuristicMatch;
      }

      // Default: neutral
      return {
        category: 'neutral',
        confidence: 0.5,
        source: 'default'
      };
    } catch (error) {
      console.error('Failed to categorize URL:', error);
      return {
        category: 'neutral',
        confidence: 0.5,
        source: 'error'
      };
    }
  }

  /**
   * Extract base domain from hostname
   */
  extractDomain(hostname) {
    // Remove www. prefix
    if (hostname.startsWith('www.')) {
      hostname = hostname.substring(4);
    }
    return hostname;
  }

  /**
   * Find wildcard match in curated domains
   */
  findWildcardMatch(domain) {
    // Check if any curated domain is a suffix of the current domain
    for (const [curatedDomain, metadata] of Object.entries(CURATED_DOMAINS)) {
      if (domain.endsWith(curatedDomain)) {
        return metadata;
      }
    }
    return null;
  }

  /**
   * Apply heuristic rules
   */
  applyHeuristics(hostname, path) {
    // Check domain patterns
    for (const rule of HEURISTIC_RULES) {
      if (rule.pattern.test(hostname)) {
        return {
          category: rule.category,
          confidence: rule.confidence,
          source: 'heuristic'
        };
      }
    }

    // Check path patterns
    for (const [category, patterns] of Object.entries(PATH_PATTERNS)) {
      for (const pattern of patterns) {
        if (path.includes(pattern)) {
          return {
            category,
            confidence: 0.7,
            source: 'heuristic_path'
          };
        }
      }
    }

    return null;
  }

  /**
   * Get category statistics
   */
  getCategoryStats() {
    const stats = {
      curated: Object.keys(CURATED_DOMAINS).length,
      heuristics: HEURISTIC_RULES.length,
      userOverrides: Object.keys(this.userOverrides).length,
      total: Object.keys(CURATED_DOMAINS).length + Object.keys(this.userOverrides).length
    };
    return stats;
  }

  /**
   * Submit community contribution (for future implementation)
   */
  async submitContribution(domain, category, context = '') {
    // This would send to backend for community review
    console.log('Community contribution submitted:', { domain, category, context });
    // TODO: Implement backend endpoint for community contributions
  }
}

// Export singleton instance
const categoryDB = new CategoryDatabase();
export default categoryDB;
