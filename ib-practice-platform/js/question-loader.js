/**
 * Performance-optimized question loader
 * - Splits questions by subject
 * - Lazy loads on demand
 * - Implements IndexedDB caching
 * - Debounces filtering operations
 */

class QuestionLoader {
  constructor() {
    this.DB_NAME = 'IVYStudy';
    this.DB_VERSION = 3;
    this.db = null;
    this.cache = new Map(); // In-memory cache for current session
    this.loadPromises = new Map(); // Track in-flight requests
    this.debounceTimers = new Map();
    this.allQuestionsPromise = null;
  }

  async initDB() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(this.DB_NAME, this.DB_VERSION);
      req.onerror = () => reject(req.error);
      req.onsuccess = () => {
        this.db = req.result;
        resolve();
      };
      req.onupgradeneeded = (e) => {
        const db = e.target.result;
        let questionsStore;
        if (!db.objectStoreNames.contains('questions')) {
          questionsStore = db.createObjectStore('questions', { keyPath: 'id' });
        } else {
          questionsStore = e.target.transaction.objectStore('questions');
          // Purge stale cached questions when schema version changes.
          questionsStore.clear();
        }

        if (!questionsStore.indexNames.contains('subject')) {
          questionsStore.createIndex('subject', 'subject', { unique: false });
        }

        if (!db.objectStoreNames.contains('metadata')) {
          db.createObjectStore('metadata', { keyPath: 'subject' });
        }
      };
    });
  }

  /**
   * Load questions for a subject (lazy load on demand)
   */
  async loadSubject(subject) {
    // Return from in-memory cache if available
    if (this.cache.has(subject)) {
      return this.cache.get(subject);
    }

    // Avoid duplicate requests
    if (this.loadPromises.has(subject)) {
      return this.loadPromises.get(subject);
    }

    const promise = this._loadSubjectImpl(subject);
    this.loadPromises.set(subject, promise);
    return promise;
  }

  async _loadSubjectImpl(subject) {
    try {
      // Try to load from IndexedDB first
      const cached = await this._getFromDB(subject);
      if (cached && cached.length > 0) {
        this.cache.set(subject, cached);
        return cached;
      }

      // Fetch from server (try subject-specific file first, then full questions.json)
      let questions = await this._fetchSubjectQuestions(subject);

      // Cache in IndexedDB for next time
      if (this.db && questions.length > 0) {
        await this._saveToDB(subject, questions);
      }

      this.cache.set(subject, questions);
      return questions;
    } catch (e) {
      // Failed to load questions for subject — will return empty array
      return [];
    } finally {
      this.loadPromises.delete(subject);
    }
  }

  async _fetchSubjectQuestions(subject) {
    const allQuestions = await this._fetchAllQuestions();
    return allQuestions.filter((q) => q.subject === subject);
  }

  _getPracticeBasePath() {
    const path = window.location.pathname || '/';
    if (path.includes('/ib-practice-platform')) {
      return '/ib-practice-platform/';
    }
    return './';
  }

  async _fetchAllQuestions() {
    if (this.allQuestionsPromise) {
      const cached = await this.allQuestionsPromise;
      if (cached && cached.length > 0) return cached;
      // Previous fetch returned empty — retry
      this.allQuestionsPromise = null;
    }

    const base = this._getPracticeBasePath();
    const fallbacks = [
      `${base}questions.json?v=${Date.now()}`,
      'questions.json?v=' + Date.now(),
      '/questions.json?v=' + Date.now(),
    ];

    this.allQuestionsPromise = (async () => {
      for (const url of fallbacks) {
        try {
          const response = await fetch(url, { cache: 'no-store' });
          if (!response.ok) continue;

          const data = await response.json();
          const questions = Array.isArray(data) ? data : data.questions || [];
          if (questions.length > 0) {
            return questions;
          }
        } catch (e) {
          // Try next fallback
        }
      }
      return [];
    })();

    return this.allQuestionsPromise;
  }

  async _getFromDB(subject) {
    if (!this.db) return null;
    return new Promise((resolve) => {
      const tx = this.db.transaction(['questions'], 'readonly');
      const store = tx.objectStore('questions');
      const req = store.index('subject').getAll(subject);
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => resolve(null);
    });
  }

  async _saveToDB(subject, questions) {
    if (!this.db) return;
    return new Promise((resolve) => {
      const tx = this.db.transaction(['questions'], 'readwrite');
      const store = tx.objectStore('questions');
      questions.forEach((q) => store.put(q));
      tx.oncomplete = () => resolve();
      tx.onerror = () => resolve(); // Fail silently
    });
  }

  /**
   * Filter questions with debouncing
   */
  debounceFilter(subject, filters, callback, delay = 300) {
    const key = `${subject}:${JSON.stringify(filters)}`;
    if (this.debounceTimers.has(key)) {
      clearTimeout(this.debounceTimers.get(key));
    }
    const timer = setTimeout(() => {
      this.filterQuestions(subject, filters).then(callback);
      this.debounceTimers.delete(key);
    }, delay);
    this.debounceTimers.set(key, timer);
  }

  /**
   * Filter questions by criteria
   */
  async filterQuestions(subject, filters = {}) {
    const questions = await this.loadSubject(subject);

    return questions.filter((q) => {
      if (filters.difficulty && q.difficulty !== filters.difficulty) return false;
      if (filters.topic && q.topic !== filters.topic) return false;
      if (filters.subtopic && q.subtopic !== filters.subtopic) return false;
      if (filters.type && q.type !== filters.type) return false;
      return true;
    });
  }

  /**
   * Prefetch related subjects for faster navigation
   */
  async prefetch(subjects) {
    return Promise.all(subjects.map((s) => this.loadSubject(s)));
  }

  /**
   * Clear cache (useful for memory management on large sessions)
   */
  clearMemoryCache() {
    this.cache.clear();
  }
}

// Singleton instance available via qLoader in optimization-adapter.js
