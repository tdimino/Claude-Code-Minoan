# Troubleshooting Guide

Common issues and solutions for Nano Banana Pro API usage.

## Table of Contents

- [Authentication Issues](#authentication-issues)
- [Rate Limiting](#rate-limiting)
- [Generation Errors](#generation-errors)
- [Quality Issues](#quality-issues)
- [Regional Restrictions](#regional-restrictions)
- [Billing Issues](#billing-issues)

## Authentication Issues

### Invalid API Key

**Error:**
```json
{
  "error": {
    "code": 401,
    "message": "API key not valid"
  }
}
```

**Solutions:**
1. Verify API key format starts with `AIza`
2. Check for extra spaces or newlines in key
3. Regenerate key in Google AI Studio
4. Verify key is for correct project

**Test:**
```bash
python test_connection.py --api-key YOUR_KEY
```

### Permission Denied

**Error:**
```json
{
  "error": {
    "code": 403,
    "message": "Permission denied"
  }
}
```

**Solutions:**
1. Enable billing in Google Cloud Console
2. Verify API is enabled for your project
3. Check if account has required permissions
4. Ensure you're not in restricted region

## Rate Limiting

### Request Quota Exceeded

**Error:**
```json
{
  "error": {
    "code": 429,
    "message": "Resource exhausted"
  }
}
```

### Solutions

#### 1. Implement Exponential Backoff

```python
import time

def make_request_with_retry(request_func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return request_func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise

            # Exponential backoff: 1s, 2s, 4s
            wait_time = 2 ** attempt
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
```

#### 2. Implement Request Queue

```python
from queue import Queue
from threading import Thread
import time

class RequestQueue:
    def __init__(self, rate_limit_per_minute=60):
        self.queue = Queue()
        self.rate_limit = rate_limit_per_minute
        self.min_interval = 60.0 / rate_limit_per_minute

    def add_request(self, request):
        self.queue.put(request)

    def process(self):
        while not self.queue.empty():
            request = self.queue.get()
            request.execute()
            time.sleep(self.min_interval)
```

#### 3. Upgrade to Paid Tier

Free tier limits:
- ~100 requests/day
- 2-5 requests/minute

Paid tier limits:
- Unlimited daily (subject to quota)
- 60 requests/minute
- 10 concurrent requests

### Daily Quota Exceeded

**Error Message:**
```
Quota exceeded for quota metric 'Generate requests' and limit 'Generate requests per day'
```

**Solutions:**
1. Wait until quota resets (midnight Pacific Time)
2. Upgrade to paid tier
3. Request quota increase in Google Cloud Console
4. Implement request caching to reduce duplicate requests

## Generation Errors

### Model Not Found (404)

**Error:**
```json
{
  "error": {
    "code": 404,
    "message": "Model not found"
  }
}
```

**Common Causes:**
1. Incorrect model name
2. Model not available in your region
3. Geo-blocking (Europe, Middle East, Africa)

**Solutions:**
1. Verify model name: `gemini-3-pro-image-preview`
2. Use VPN if geo-blocked
3. Try alternative model: `gemini-2.5-flash-image`

### Content Policy Violation

**Error:**
```json
{
  "error": {
    "code": 400,
    "message": "Content violates safety policy"
  }
}
```

**Blocked Content Types:**
- Violence or gore
- Sexual content
- Illegal activities
- Copyrighted characters without permission
- Real public figures without authorization

**Solutions:**
1. Rephrase prompt to be less explicit
2. Remove references to copyrighted characters
3. Adjust safety settings (with caution)
4. Use generic descriptions instead of specific people

### Image Generation Failed

**Error:**
```
"I'm still learning how to generate images for you"
```

**Causes:**
1. Account restrictions (age verification)
2. Geographic restrictions
3. Workspace administrator disabled feature
4. Prompt complexity or safety filters
5. Temporary service outage

**Solutions:**
1. Verify account is 18+ (check birthdate in Google Account)
2. Check if workspace admin allows image generation
3. Simplify prompt and try again
4. Start a new chat session
5. Check Google AI Studio status page
6. Try different browser/clear cache

### Timeout Errors

**Error:**
```
requests.exceptions.Timeout: Request timed out
```

**Solutions:**
1. Increase timeout: 60s for generation, 90s for editing
2. Simplify prompt (fewer details)
3. Reduce image resolution (use 1K instead of 4K)
4. Split complex requests into multiple steps
5. Try during off-peak hours

## Quality Issues

### Blurry or Low-Quality Output

**Causes:**
- Low-resolution input images
- Vague prompts
- Temperature too high
- Compression artifacts

**Solutions:**
1. Use high-resolution inputs (min 1024px)
2. Add quality modifiers to prompt:
   - "4K resolution"
   - "sharp focus"
   - "high detail"
   - "professional photography quality"
3. Lower temperature to 0.5-0.6 for more consistency
4. Request specific aspect ratio matching your needs

### Text Not Legible in Image

**Causes:**
- Text too long (>25 characters)
- Font size not specified
- Complex background

**Solutions:**
1. Keep text under 25 characters
2. Specify font properties:
   ```
   "Add text 'HELLO' in large bold sans-serif font centered on solid background"
   ```
3. Request simple background behind text
4. Use multi-turn editing to refine text placement

### Incorrect Colors or Style

**Causes:**
- Conflicting style instructions
- Vague color descriptions
- Model interpretation

**Solutions:**
1. Use specific color names or hex codes:
   - "vibrant cyan blue #00CED1"
   - "warm amber lighting 3200K"
2. Reference specific styles:
   - "Wes Anderson color palette"
   - "Studio Ghibli art style"
3. Use multi-turn editing to refine
4. Provide reference images (up to 14)

### Inconsistent Results

**Causes:**
- High temperature setting
- Ambiguous prompts
- No reference images

**Solutions:**
1. Lower temperature (0.3-0.5 for consistency)
2. Be more specific in prompts
3. Upload reference images for style consistency
4. Use the same seed (if supported in future updates)
5. Iterate with multi-turn editing

## Regional Restrictions

### Geo-Blocking

**Affected Regions:**
- Several European countries
- Middle East
- Africa

**Error:**
```
Model not available in your region
```

**Solutions:**
1. Use VPN service
2. Use third-party proxy services (e.g., Image Router)
3. Use Vertex AI if in supported region
4. Use alternative models available in your region

### Feature Not Available

**Some features may be restricted by region:**
- Person generation settings
- Certain content categories
- 4K resolution

**Check availability:**
```python
# Test with simple prompt first
client.generate_image("simple test: red circle")
```

## Billing Issues

### Billing Not Enabled

**Error:**
```
Billing must be enabled for this project
```

**Solutions:**
1. Go to Google Cloud Console
2. Navigate to Billing
3. Link billing account to project
4. Enable Gemini API billing

### Unexpected Costs

**Common Causes:**
- Generating many 4K images ($0.24 each)
- High-frequency API calls
- Not using free tier efficiently

**Cost Optimization:**
1. Use 1K/2K images for drafts ($0.134)
2. Cache results to avoid regeneration
3. Implement request queuing
4. Monitor usage in Google Cloud Console
5. Set budget alerts

### Payment Declined

**Solutions:**
1. Verify credit card is valid
2. Check billing address
3. Contact your bank about international charges
4. Try alternative payment method
5. Contact Google Cloud Support

## Browser/Client Issues

### Browser Extension Conflicts

**Symptoms:**
- Image generation menu missing
- Requests failing silently
- Unexpected errors

**Solutions:**
1. Disable ad blockers
2. Disable privacy extensions temporarily
3. Try incognito/private mode
4. Try different browser
5. Clear browser cache and cookies

### Network Issues

**Symptoms:**
- Connection timeout
- DNS resolution failures
- SSL certificate errors

**Solutions:**
1. Check internet connection
2. Try different network (e.g., mobile hotspot)
3. Disable VPN temporarily (unless needed for geo-blocking)
4. Check firewall settings
5. Verify DNS settings

## Debugging Workflow

### Step-by-Step Troubleshooting

1. **Test API Connection:**
   ```bash
   python test_connection.py --api-key YOUR_KEY
   ```

2. **Try Simple Request:**
   ```python
   response = client.generate_image("simple test: red circle")
   ```

3. **Check Response:**
   ```python
   print(json.dumps(response, indent=2))
   ```

4. **Verify Image Data:**
   ```python
   if "inlineData" in response.get("candidates", [{}])[0]:
       print("✓ Image generated successfully")
   ```

5. **Test with Verbose Logging:**
   ```bash
   python generate_image.py "test prompt" --verbose
   ```

### Getting Help

If issues persist:

1. **Check Status Page:**
   - https://status.cloud.google.com

2. **Review Documentation:**
   - https://ai.google.dev/gemini-api/docs

3. **Community Support:**
   - Stack Overflow (tag: google-gemini)
   - Reddit: r/GoogleGemini

4. **Official Support:**
   - Google AI Studio feedback button
   - Google Cloud Support (paid tiers)

5. **GitHub Issues:**
   - Check if others report similar issues
   - SDK-specific repos

## Common Error Codes Reference

| Code | Error | Common Cause | Solution |
|------|-------|--------------|----------|
| 400 | Bad Request | Invalid JSON or parameters | Check request format |
| 401 | Unauthorized | Invalid/missing API key | Verify API key |
| 403 | Forbidden | Billing or permissions | Enable billing |
| 404 | Not Found | Wrong model name or geo-block | Check model name/region |
| 429 | Rate Limited | Too many requests | Implement backoff |
| 500 | Internal Error | Server issue | Retry with backoff |
| 503 | Service Unavailable | Temporary outage | Wait and retry |

## Performance Optimization

### Reduce Latency

1. **Use appropriate resolution:**
   - 1K for previews (fastest)
   - 2K for balanced quality
   - 4K only for final output

2. **Optimize prompts:**
   - Be concise but specific
   - Avoid overly long prompts

3. **Geographic proximity:**
   - Use nearest data center
   - Consider Vertex AI regional endpoints

4. **Caching:**
   - Cache identical requests
   - Store frequently used results

### Maximize Quality

1. **Iterative refinement:**
   - Start simple
   - Use multi-turn editing

2. **Reference images:**
   - Provide style references
   - Use up to 14 images

3. **Optimal settings:**
   - Temperature: 0.7 (balanced)
   - Resolution: 2K minimum
   - Aspect ratio: Match intended use
