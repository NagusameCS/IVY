// Cloudflare Worker for Desmos API Proxy
// Deploy this at: your-worker.your-subdomain.workers.dev

const DESMOS_API_KEY = 'YOUR_ACTUAL_DESMOS_API_KEY_HERE'; // Set this in Worker environment variables
const ALLOWED_ORIGINS = [
    'https://ivystudy.org',
    'https://www.ivystudy.org', 
    'http://localhost:8080',
    'http://127.0.0.1:8080'
];

// Rate limiting configuration
const RATE_LIMITS = {
    windowMs: 60 * 1000, // 1 minute
    maxRequests: 100     // requests per window per IP
};

export default {
    async fetch(request, env, ctx) {
        // CORS preflight
        if (request.method === 'OPTIONS') {
            return handleCORS(request);
        }
        
        // Check origin
        const origin = request.headers.get('Origin');
        if (!ALLOWED_ORIGINS.includes(origin)) {
            return new Response('Forbidden', { status: 403 });
        }
        
        // Rate limiting
        const clientIP = request.headers.get('CF-Connecting-IP');
        const rateLimitResult = await checkRateLimit(clientIP, env);
        if (!rateLimitResult.allowed) {
            return new Response('Rate limit exceeded', { 
                status: 429,
                headers: {
                    'Retry-After': '60',
                    'X-RateLimit-Limit': RATE_LIMITS.maxRequests.toString(),
                    'X-RateLimit-Remaining': '0',
                    'X-RateLimit-Reset': rateLimitResult.resetTime.toString()
                }
            });
        }
        
        // Parse request
        const url = new URL(request.url);
        const path = url.pathname;
        
        // Route handling
        if (path.startsWith('/calculator/')) {
            return handleCalculatorAPI(request, env);
        } else if (path.startsWith('/graphing/')) {
            return handleGraphingAPI(request, env);
        } else if (path === '/health') {
            return new Response('OK', { status: 200 });
        }
        
        return new Response('Not Found', { status: 404 });
    }
};

async function handleCalculatorAPI(request, env) {
    try {
        const apiKey = env.DESMOS_API_KEY || DESMOS_API_KEY;
        const url = new URL(request.url);
        
        // Build Desmos API URL
        const desmosUrl = `https://www.desmos.com/api/v1${url.pathname}${url.search}`;
        
        // Forward request to Desmos
        const desmosRequest = new Request(desmosUrl, {
            method: request.method,
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'User-Agent': 'IVYSTUDY/1.0'
            },
            body: request.method !== 'GET' ? await request.text() : undefined
        });
        
        const desmosResponse = await fetch(desmosRequest);
        const responseBody = await desmosResponse.text();
        
        // Return response with CORS headers
        return new Response(responseBody, {
            status: desmosResponse.status,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': request.headers.get('Origin'),
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '86400',
                'Cache-Control': 'public, max-age=300' // 5 minute cache
            }
        });
        
    } catch (error) {
        return new Response(JSON.stringify({ 
            error: 'API request failed',
            message: error.message 
        }), { 
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

async function handleGraphingAPI(request, env) {
    try {
        const apiKey = env.DESMOS_API_KEY || DESMOS_API_KEY;
        const body = await request.json();
        
        // Proxy to Desmos Graphing API
        const desmosResponse = await fetch('https://www.desmos.com/api/v1/calculator', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'User-Agent': 'IVYSTUDY/1.0'
            },
            body: JSON.stringify({
                ...body,
                // Add any default options
                options: {
                    keypad: false,
                    expressions: true,
                    settingsMenu: false,
                    ...body.options
                }
            })
        });
        
        const result = await desmosResponse.json();
        
        return new Response(JSON.stringify(result), {
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': request.headers.get('Origin'),
                'Cache-Control': 'public, max-age=3600' // 1 hour cache
            }
        });
        
    } catch (error) {
        return new Response(JSON.stringify({ 
            error: 'Graphing API failed',
            message: error.message 
        }), { 
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

async function checkRateLimit(clientIP, env) {
    const now = Date.now();
    const windowStart = now - RATE_LIMITS.windowMs;
    const key = `rate_limit:${clientIP}:${Math.floor(now / RATE_LIMITS.windowMs)}`;
    
    try {
        // Get current count from KV storage (if using Cloudflare KV)
        const stored = await env.RATE_LIMIT_KV?.get(key);
        const count = stored ? parseInt(stored) : 0;
        
        if (count >= RATE_LIMITS.maxRequests) {
            return {
                allowed: false,
                resetTime: windowStart + RATE_LIMITS.windowMs
            };
        }
        
        // Increment counter
        await env.RATE_LIMIT_KV?.put(key, (count + 1).toString(), {
            expirationTtl: Math.ceil(RATE_LIMITS.windowMs / 1000)
        });
        
        return { allowed: true };
        
    } catch (error) {
        // If KV fails, allow request (fail open)
        console.error('Rate limit check failed:', error);
        return { allowed: true };
    }
}

function handleCORS(request) {
    return new Response(null, {
        status: 204,
        headers: {
            'Access-Control-Allow-Origin': request.headers.get('Origin'),
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        }
    });
}