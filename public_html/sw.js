// Service Worker for offline caching and performance
const STATIC_CACHE = 'ivystudy-static-v1';
const DYNAMIC_CACHE = 'ivystudy-dynamic-v1';

const STATIC_ASSETS = [
    '/',
    '/home',
    '/timer',
    '/exemplars',
    '/teachers',
    '/js/themeManager.js',
    '/js/componentLoader.js',
    '/components/head.html',
    '/components/styles.html',
    '/components/navigation.html',
    '/components/footer.html',
    '/components/scripts.html',
    '/manifest.json',
    'https://cdn.tailwindcss.com',
    'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap',
    'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200'
];

// Install - cache static assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => cache.addAll(STATIC_ASSETS))
            .then(() => self.skipWaiting())
    );
});

// Activate - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch - implement caching strategies
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') return;
    
    // API requests - network first with cache fallback
    if (url.pathname.startsWith('/api')) {
        event.respondWith(networkFirst(request, DYNAMIC_CACHE));
        return;
    }
    
    // Font files - cache first
    if (url.hostname.includes('googleapis') || url.hostname.includes('gstatic')) {
        event.respondWith(cacheFirst(request, STATIC_CACHE));
        return;
    }
    
    // Components - stale while revalidate
    if (url.pathname.startsWith('/components/')) {
        event.respondWith(staleWhileRevalidate(request, DYNAMIC_CACHE));
        return;
    }
    
    // Images - cache first
    if (request.destination === 'image') {
        event.respondWith(cacheFirst(request, DYNAMIC_CACHE));
        return;
    }
    
    // Pages - stale while revalidate
    event.respondWith(staleWhileRevalidate(request, DYNAMIC_CACHE));
});

// Cache strategies
async function cacheFirst(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cached = await cache.match(request);
    
    if (cached) return cached;
    
    try {
        const response = await fetch(request);
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        return new Response('Offline', { status: 503 });
    }
}

async function networkFirst(request, cacheName) {
    const cache = await caches.open(cacheName);
    
    try {
        const response = await fetch(request);
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        const cached = await cache.match(request);
        return cached || new Response('Offline', { status: 503 });
    }
}

async function staleWhileRevalidate(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cached = await cache.match(request);
    
    const fetchPromise = fetch(request).then(response => {
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    }).catch(() => cached);
    
    return cached || fetchPromise;
}

// Background sync for analytics
self.addEventListener('sync', event => {
    if (event.tag === 'analytics') {
        event.waitUntil(syncAnalytics());
    }
});

async function syncAnalytics() {
    // Sync any pending analytics when back online
    try {
        await fetch('/api');
    } catch (error) {
        // Analytics sync failed — will retry on next sync event
    }
}