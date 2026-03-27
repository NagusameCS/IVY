/**
 * Memory & Performance Profiler
 * Monitors memory usage and loading times for optimization verification
 * 
 * Usage:
 * Open browser console and run: profiler.start()
 * Then use the app normally
 * Call: profiler.report() to see metrics
 */

const profiler = {
  metrics: {
    pageLoadTime: 0,
    subjectLoadTimes: {},
    memorySnapshots: [],
    cacheHits: 0,
    cacheMisses: 0,
    networkRequests: 0,
  },

  start() {
    console.log('🚀 Performance profiler started');
    this.metrics.pageLoadTime = performance.now();
    this.setupMemoryMonitoring();
    this.setupNetworkMonitoring();
  },

  setupMemoryMonitoring() {
    if (!performance.memory) {
      console.warn('Memory monitoring not available (try Chrome)');
      return;
    }

    setInterval(() => {
      const mem = performance.memory;
      this.metrics.memorySnapshots.push({
        timestamp: new Date().toLocaleTimeString(),
        usedJSHeapSize: (mem.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
        totalJSHeapSize: (mem.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
        limit: (mem.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB',
      });
    }, 5000);
  },

  setupNetworkMonitoring() {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const url = args[0];
      const startTime = performance.now();

      try {
        const response = await originalFetch(...args);
        const elapsed = (performance.now() - startTime).toFixed(2);

        if (url.includes('questions')) {
          console.log(
            `📦 Loaded ${url.split('/').pop()}: ${elapsed}ms`,
            `(${response.headers.get('content-length')} bytes)`
          );
          this.metrics.networkRequests++;
        }

        return response;
      } catch (e) {
        console.error(`❌ Network error: ${url}`, e);
        throw e;
      }
    };
  },

  trackSubjectLoad(subject, duration) {
    this.metrics.subjectLoadTimes[subject] = duration;
    console.log(`✓ Subject ${subject} loaded in ${duration.toFixed(2)}ms`);
  },

  trackCacheHit(subject) {
    this.metrics.cacheHits++;
    console.log(`⚡ Cache hit for ${subject} (${this.metrics.cacheHits} total)`);
  },

  trackCacheMiss(subject) {
    this.metrics.cacheMisses++;
    console.log(`🔄 Cache miss for ${subject} (${this.metrics.cacheMisses} total)`);
  },

  report() {
    const elapsed = (performance.now() - this.metrics.pageLoadTime).toFixed(2);

    console.clear();
    console.log('%c=== PERFORMANCE REPORT ===', 'font-size: 16px; font-weight: bold;');

    // Page load time
    console.log('\n📊 Page Load Metrics:');
    console.log(`  Page load time: ${elapsed}ms`);
    console.log(`  Network requests: ${this.metrics.networkRequests}`);
    console.log(`  Cache hits: ${this.metrics.cacheHits}`);
    console.log(`  Cache misses: ${this.metrics.cacheMisses}`);
    const hitRate = (
      (this.metrics.cacheHits / (this.metrics.cacheHits + this.metrics.cacheMisses)) *
      100
    ).toFixed(1);
    if (this.metrics.cacheHits + this.metrics.cacheMisses > 0) {
      console.log(`  Cache hit rate: ${hitRate}%`);
    }

    // Subject load times
    if (Object.keys(this.metrics.subjectLoadTimes).length > 0) {
      console.log('\n⏱️  Subject Load Times:');
      for (const [subject, time] of Object.entries(this.metrics.subjectLoadTimes)) {
        console.log(`  ${subject}: ${time.toFixed(2)}ms`);
      }
    }

    // Memory snapshots
    if (this.metrics.memorySnapshots.length > 0) {
      console.log('\n💾 Memory Snapshots (last 5):');
      const recent = this.metrics.memorySnapshots.slice(-5);
      for (const snap of recent) {
        console.log(
          `  ${snap.timestamp}: ${snap.usedJSHeapSize} / ${snap.totalJSHeapSize} (limit: ${snap.limit})`
        );
      }
    }

    // Recommendations
    console.log('\n💡 Recommendations:');
    if (this.metrics.networkRequests > 10) {
      console.log('  • High network requests - consider pre-chunking questions.json');
    }
    if (hitRate < 50) {
      console.log('  • Low cache hit rate - IndexedDB might not be working');
    }
    if (this.metrics.memorySnapshots.length > 0) {
      const latest = this.metrics.memorySnapshots[this.metrics.memorySnapshots.length - 1];
      const used = parseFloat(latest.usedJSHeapSize);
      const limit = parseFloat(latest.limit);
      if (used > limit * 0.8) {
        console.log('  • High memory usage - consider loading fewer questions per session');
      }
    }

    console.log('\n%cEnd of Report', 'color: gray; font-style: italic;');
  },

  // Export metrics as JSON for analysis
  export() {
    const data = {
      timestamp: new Date().toISOString(),
      totalRuntime: (performance.now() - this.metrics.pageLoadTime).toFixed(2) + 'ms',
      metrics: this.metrics,
    };
    console.log('📋 Metrics JSON:', JSON.stringify(data, null, 2));
    return data;
  },
};

// Hook into question loader if available
if (typeof qLoader !== 'undefined') {
  const originalLoadSubject = qLoader.loadSubject.bind(qLoader);
  qLoader.loadSubject = async function (subject) {
    const startTime = performance.now();
    const isCached = this.cache.has(subject);

    const result = await originalLoadSubject(subject);

    const duration = performance.now() - startTime;
    profiler.trackSubjectLoad(subject, duration);

    if (isCached) {
      profiler.trackCacheHit(subject);
    } else {
      profiler.trackCacheMiss(subject);
    }

    return result;
  };
}

console.log('✅ Profiler loaded. Run: profiler.start() then profiler.report()');
