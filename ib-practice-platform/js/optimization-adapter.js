/**
 * Integration patch for performance optimizations
 * Modifies the existing question loading and practice flows to use lazy loading
 */

// Debug logging — silent in production
const _dbg = location.hostname === 'localhost' || location.hostname === '127.0.0.1'
  ? console.log.bind(console, '[opt]')
  : () => {};

// Initialize the question loader on page load
let qLoader = null;

async function initializeQuestionLoader() {
  qLoader = new QuestionLoader();
  try {
    await qLoader.initDB();
    _dbg('IndexedDB initialized for question caching');
  } catch (e) {
    _dbg('IndexedDB not available, using memory cache only:', e);
  }
}

/**
 * Enhanced loadQuestions that uses lazy loading
 * Falls back to full fetch only if subject-specific files not available
 */
async function loadQuestionsOptimized() {
  if (!qLoader) {
    await initializeQuestionLoader();
  }

  try {
    // Load all questions upfront so state.loadedQuestions is populated
    const allQuestions = await qLoader._fetchAllQuestions();
    if (allQuestions && allQuestions.length > 0) {
      state.loadedQuestions = allQuestions;
      _dbg(`Optimized loader: ${allQuestions.length} questions ready`);
    } else {
      // Clear cached empty promise so next attempt retries the fetch
      qLoader.allQuestionsPromise = null;
      return false;
    }
    
    return true;
  } catch (e) {
    _dbg('Failed to initialize optimized loading:', e);
    if (qLoader) qLoader.allQuestionsPromise = null;
    return false;
  }
}

/**
 * Enhanced startPractice with lazy loading
 */
async function startPracticeOptimized() {
  // Ensure loader is initialized
  if (!qLoader) {
    await initializeQuestionLoader();
  }

  const subjectKeys = state.selectedSubject === 'math_ai'
    ? ['math_ai', 'math_aa']
    : [state.selectedSubject];

  // Load questions for selected subjects (lazy load here)
  let available = [];
  for (const subject of subjectKeys) {
    try {
      const questions = await qLoader.loadSubject(subject);
      available = available.concat(questions);
    } catch (e) {
      _dbg(`Failed to load ${subject}:`, e);
    }
  }

  // If no questions loaded with optimized method, fall back to full load
  if (available.length === 0) {
    _dbg('Lazy load returned no results, falling back to full questions.json');
    try {
      const basePath = window.location.pathname.includes('/ib-practice-platform') ? '/ib-practice-platform/' : './';
      const response = await fetch(`${basePath}questions.json`);
      const data = await response.json();
      available = Array.isArray(data) ? data : (data.questions || EXAMPLE_QUESTIONS);
    } catch (e) {
      available = EXAMPLE_QUESTIONS;
    }
  }

  // Apply filters with debouncing
  const filters = {};
  if (state.difficulty !== 'all') filters.difficulty = state.difficulty;
  if (state.selectedSubtopics.size > 0) {
    // For topic filtering, we'll do it post-load since topics vary by subject
  }

  // Apply difficulty filter
  let filtered = available.filter(q => {
    if (filters.difficulty && q.difficulty !== filters.difficulty) return false;
    const key = q.topic + ':' + q.subtopic;
    if (state.selectedSubtopics.size > 0 && !state.selectedSubtopics.has(key)) return false;
    return true;
  });

  // Fallback to subject only if no matches
  if (filtered.length === 0) {
    filtered = available;
  }

  // Shuffle and use all available questions
  shuffleArray(filtered);
  state.questions = filtered;
  state.currentQuestionIndex = 0;
  state.answers = {};
  state.flags = new Set();
  state.reviewMode = false;
  state.totalQuestions = state.questions.length;

  // Timer setup
  state.timerSeconds = 0;
  if (state.timerInterval) clearInterval(state.timerInterval);
  const timerEl = document.getElementById('timer-display');
  if (state.timerEnabled) {
    timerEl.style.display = 'flex';
    state.timerInterval = setInterval(() => {
      state.timerSeconds++;
      document.getElementById('timer-value').textContent = formatTime(state.timerSeconds);
    }, 1000);
  } else {
    timerEl.style.display = 'none';
  }

  // Update UI
  document.getElementById('practice-subject-label').textContent = getSubjectName(state.selectedSubject);
  updateBreadcrumb([
    { label: getSubjectName(state.selectedSubject), action: () => navigate('topics', state.selectedSubject) },
    { label: 'Practice' }
  ]);

  renderQuestion();
  renderNavPills();
  updateProgress();
}

/**
 * Pagination utility for infinite scrolling
 * Call this when user scrolls to bottom of question list
 */
async function loadMoreQuestions() {
  if (!state.questions || state.currentQuestionIndex >= state.questions.length) {
    return; // Already loaded all filtered results
  }

  // If we're close to the end, queue the next subject
  const remainingQuestions = state.questions.length - state.currentQuestionIndex;
  if (remainingQuestions < 10) {
    // Could implement queue for next subject here
    _dbg('Approaching end of current batch, would load next subject');
  }
}

/**
 * Debounced filter update for performance
 */
function applyFiltersDebounced(subject, filters) {
  if (!qLoader) return;

  qLoader.debounceFilter(subject, filters, (filtered) => {
    // Update state and UI with filtered results
    shuffleArray(filtered);
    state.questions = filtered;
    state.currentQuestionIndex = 0;
    renderQuestion();
    updateProgress();
  }, 300);
}

/**
 * Clear memory cache if needed (useful for long sessions)
 */
function clearQuestionCache() {
  if (qLoader) {
    qLoader.clearMemoryCache();
    _dbg('Question memory cache cleared');
  }
}

/**
 * Initialize optimization on DOM ready
 * Called from main DOMContentLoaded handler
 */
async function initOptimizations() {
  try {
    await initializeQuestionLoader();
    await loadQuestionsOptimized();
    _dbg('Performance optimizations initialized');
  } catch (e) {
    _dbg('Failed to initialize optimizations:', e);
  }
}
