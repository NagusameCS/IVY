/**
 * CDN Router - Intelligent routing for static assets
 * Falls back: Local → Cloudflare → Original CDN → Offline
 * Reduces GitHub dependence and improves reliability
 */

class CDNRouter {
  constructor(config = {}) {
    this.config = {
      useLocal: false,
      localPath: "/cdn-cache",
      cloudflareZone: config.cloudflareZone,
      enableFallbacks: true,
      cacheTime: 24 * 60 * 60 * 1000, // 24 hours
      ...config,
    };

    this.cache = new Map();
    this.loadingPromises = new Map();
    this.stats = {
      localHits: 0,
      cloudflareHits: 0,
      cdnHits: 0,
      failures: 0,
    };

    this._timeoutMs = 2500;
  }

  /**
   * Build CDN resource URL with intelligent routing
   */
  async getResourceUrl(originalUrl, resourceType = "library") {
    // Check cache first
    if (this.cache.has(originalUrl)) {
      const cached = this.cache.get(originalUrl);
      if (Date.now() - cached.timestamp < this.config.cacheTime) {
        this.stats.localHits++;
        return cached.url;
      }
    }

    // Avoid duplicate requests
    if (this.loadingPromises.has(originalUrl)) {
      return this.loadingPromises.get(originalUrl);
    }

    const promise = this._resolveUrl(originalUrl, resourceType);
    this.loadingPromises.set(originalUrl, promise);

    try {
      const url = await promise;
      this.cache.set(originalUrl, { url, timestamp: Date.now() });
      return url;
    } finally {
      this.loadingPromises.delete(originalUrl);
    }
  }

  async _resolveUrl(originalUrl, resourceType) {
    const routes = [
      () => this._tryLocalCache(originalUrl),
      () => this._tryCloudflare(originalUrl),
      () => this._tryDirectFallback(originalUrl),
      () => this._useOriginal(originalUrl),
    ];

    for (const route of routes) {
      try {
        const url = await route();
        if (url) {
          console.log(`✓ CDN ${originalUrl.split("/").pop()}: ${this._getSource(url)}`);
          return url;
        }
      } catch (e) {
        // Try next route
      }
    }

    // All fallbacks failed
    this.stats.failures++;
    console.warn(`✗ CDN ${originalUrl}: all routes failed`);
    return originalUrl; // Last resort
  }

  async _tryLocalCache(url) {
    if (!this.config.useLocal) return null;

    // Try to fetch from local cache endpoint
    try {
      const cacheKey = this._urlToKey(url);
      const response = await fetch(`${this.config.localPath}/${cacheKey}`, {
        cache: "force-cache",
      });

      if (response.ok) {
        const blob = await response.blob();
        return URL.createObjectURL(blob);
      }
    } catch (e) {
      //  Not in local cache
    }

    return null;
  }

  async _tryCloudflare(url) {
    // Disabled unless a real Cloudflare zone mapping is configured.
    if (!this.config.cloudflareZone) return null;
    return null;
  }

  async _tryDirectFallback(url) {
    // Only try validated mirror variants to avoid noisy/slow probes.
    let mirrors = [];
    if (url.includes("cdn.jsdelivr.net")) {
      mirrors = [url.replace("cdn.jsdelivr.net", "fastly.jsdelivr.net")];
    } else if (url.includes("cdnjs.cloudflare.com")) {
      mirrors = [url.replace("cdnjs.cloudflare.com", "cdnjs.loli.net")];
    } else {
      return null;
    }

    for (const mirror of mirrors) {
      try {
        if (mirror === url) continue;
        const response = await fetch(mirror, { signal: AbortSignal.timeout(this._timeoutMs) });
        if (response.ok) {
          this.stats.cdnHits++;
          return mirror;
        }
      } catch (e) {
        // Mirror unavailable
      }
    }

    return null;
  }

  _useOriginal(url) {
    // Fallback to original URL as last resort
    return Promise.resolve(url);
  }

  _urlToKey(url) {
    // Convert URL to cache key
    return url.replace(/[^a-z0-9]/gi, "_").substr(0, 100);
  }

  _getSource(url) {
    if (url.startsWith("blob:")) return "local";
    if (url.includes("cloudflare")) return "Cloudflare";
    if (url.includes("jsdelivr")) return "jsDelivr";
    if (url.includes("cdnjs")) return "cdnjs";
    return "original";
  }

  /**
   * Preload and cache critical libraries
   */
  async precacheLibraries(urls) {
    console.log(`📦 Precaching ${urls.length} libraries...`);
    const promises = urls.map((url) => this.getResourceUrl(url));
    await Promise.allSettled(promises);
    console.log(`✓ Precaching complete`);
  }

  /**
   * Get statistics about CDN performance
   */
  getStats() {
    return {
      ...this.stats,
      total:
        this.stats.localHits +
        this.stats.cloudflareHits +
        this.stats.cdnHits +
        this.stats.failures,
      successRate:
        ((this.stats.localHits +
          this.stats.cloudflareHits +
          this.stats.cdnHits) /
          (this.stats.localHits +
            this.stats.cloudflareHits +
            this.stats.cdnHits +
            this.stats.failures) *
          100).toFixed(1) + "%",
    };
  }

  /**
   * Update script src attributes dynamically
   */
  async applyToScriptTag(scriptTag) {
    const src = scriptTag.getAttribute("src");
    if (!src) return;

    const newUrl = await this.getResourceUrl(src);
    if (newUrl !== src) {
      scriptTag.setAttribute("src", newUrl);
      console.log(`Updated script: ${src.split("/").pop()}`);
    }
  }

  /**
   * Update stylesheet link attributes dynamically
   */
  async applyToLinkTag(linkTag) {
    const href = linkTag.getAttribute("href");
    if (!href) return;

    const newUrl = await this.getResourceUrl(href);
    if (newUrl !== href) {
      linkTag.setAttribute("href", newUrl);
      console.log(`Updated stylesheet: ${href.split("/").pop()}`);
    }
  }

  /**
   * Scan document and optimize all CDN references
   */
  async optimizeDocument() {
    console.log("🔄 Optimizing CDN references in document...");

    // Scripts
    const scripts = document.querySelectorAll('script[src*="cdn"], script[src*="jsdelivr"], script[src*="cdnjs"]');
    for (const script of scripts) {
      await this.applyToScriptTag(script);
    }

    // Stylesheets
    const links = document.querySelectorAll('link[href*="cdn"], link[href*="jsdelivr"], link[href*="cdnjs"]');
    for (const link of links) {
      await this.applyToLinkTag(link);
    }

    console.log(`✓ CDN optimization complete (${this.getStats().total} resources)`);
  }
}

// Export singleton
const cdnRouter = new CDNRouter();

// Preload critical libraries on page load
window.addEventListener("DOMContentLoaded", async () => {
  await cdnRouter.precacheLibraries([
    "https://cdn.tailwindcss.com",
    "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js",
  ]);

  // Optionally optimize all references
  // await cdnRouter.optimizeDocument();
});
