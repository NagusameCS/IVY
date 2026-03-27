# Cloudflare Worker Setup for Desmos API

## 1. Create the Worker

1. **Go to Cloudflare Dashboard** → Workers & Pages
2. **Create a new Worker** 
3. **Name it**: `ivystudy-desmos-api`
4. **Copy the code** from `cloudflare-worker.js`

## 2. Set Environment Variables

In your worker settings, add:
```
DESMOS_API_KEY = your_actual_desmos_api_key_here
```

## 3. Optional: Set up KV Storage (for rate limiting)

1. **Create KV Namespace**: `ivystudy-rate-limits`
2. **Bind to worker** as `RATE_LIMIT_KV`

## 4. Configure Custom Domain (Optional)

Set up: `api.ivystudy.org` → points to your worker

## 5. Update Your Frontend Code

Replace direct Desmos API calls with:

```javascript
// OLD: Direct API call
const response = await fetch('https://www.desmos.com/api/v1/calculator', {
    headers: { 'Authorization': `Bearer ${API_KEY}` }
});

// NEW: Via your worker
const response = await fetch('https://your-worker.workers.dev/calculator/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ /* your data */ })
});
```

## 6. Worker Endpoints

- `GET /health` - Health check
- `POST /calculator/*` - Calculator API proxy
- `POST /graphing/*` - Graphing API proxy

## 7. Security Features

✅ **CORS protection** - Only allows your domains  
✅ **Rate limiting** - 100 requests/minute per IP  
✅ **API key security** - Hidden from frontend  
✅ **Error handling** - Graceful fallbacks  
✅ **Caching** - 5min cache for API responses  

## 8. Testing

```bash
# Test health endpoint
curl https://your-worker.workers.dev/health

# Test calculator endpoint
curl -X POST https://your-worker.workers.dev/calculator/ \
  -H "Content-Type: application/json" \
  -d '{"expression": "x^2"}'
```

## 9. Deployment

The worker will automatically deploy when you save it in the Cloudflare dashboard.

## 10. Monitoring

- Check worker analytics in Cloudflare dashboard
- Monitor rate limit hits
- Watch for API errors

This setup provides:
- **Security**: API key hidden from users
- **Performance**: Caching and CDN 
- **Reliability**: Rate limiting and error handling
- **Scalability**: Cloudflare's global network