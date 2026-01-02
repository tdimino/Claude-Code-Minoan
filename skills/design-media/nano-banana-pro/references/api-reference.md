# Nano Banana Pro API Reference

Complete API documentation for Google's Nano Banana Pro (Gemini 3 Pro Image).

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Request Format](#request-format)
- [Response Format](#response-format)
- [Configuration Options](#configuration-options)
- [Pricing](#pricing)
- [Rate Limits](#rate-limits)

## Authentication

### API Key

All requests require a Gemini API key passed in the header:

```bash
x-goog-api-key: YOUR_API_KEY
```

### Obtaining an API Key

1. **Google AI Studio** (Free tier available):
   - Visit https://aistudio.google.com
   - Sign in with Google account
   - Click "Get API key" in sidebar
   - Generate new key

2. **Vertex AI** (Enterprise):
   - Go to Google Cloud Console
   - Navigate to Vertex AI > Model Garden
   - Find "Gemini 3 Pro Image"
   - Enable API and generate credentials

### Environment Variable

Store your API key securely:

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

## Endpoints

### Base URL

```
https://generativelanguage.googleapis.com/v1beta/models
```

### Generate Content

```
POST /v1beta/models/{model}:generateContent
```

**Supported Models:**
- `gemini-3-pro-image-preview` (Nano Banana Pro)
- `gemini-2.5-flash-image` (Nano Banana)

## Request Format

### Basic Structure

```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Your prompt here"
        }
      ]
    }
  ],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "temperature": 0.7,
    "maxOutputTokens": 1024,
    "imageConfig": {
      "aspectRatio": "16:9"
    }
  }
}
```

### With Image Input (for editing)

```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Edit instruction"
        },
        {
          "inlineData": {
            "mimeType": "image/jpeg",
            "data": "base64_encoded_image_data"
          }
        }
      ]
    }
  ],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9"
    }
  }
}
```

### With Multiple Reference Images

```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Generate based on these references"
        },
        {
          "inlineData": {
            "mimeType": "image/jpeg",
            "data": "base64_image_1"
          }
        },
        {
          "inlineData": {
            "mimeType": "image/png",
            "data": "base64_image_2"
          }
        }
      ]
    }
  ],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"]
  }
}
```

## Response Format

### Success Response

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "Description of the generated image..."
          },
          {
            "inlineData": {
              "mimeType": "image/jpeg",
              "data": "base64_encoded_image_data"
            }
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "safetyRatings": [
        {
          "category": "HARM_CATEGORY_HATE_SPEECH",
          "probability": "NEGLIGIBLE"
        }
      ]
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 45,
    "candidatesTokenCount": 120,
    "totalTokenCount": 165
  }
}
```

### Error Response

```json
{
  "error": {
    "code": 400,
    "message": "Invalid argument provided",
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.BadRequest",
        "fieldViolations": [
          {
            "field": "contents",
            "description": "Must provide at least one part"
          }
        ]
      }
    ]
  }
}
```

## Configuration Options

### generationConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `responseModalities` | array | `["TEXT", "IMAGE"]` | Output types to generate |
| `temperature` | float | `0.7` | Sampling temperature (0.0-1.0) |
| `maxOutputTokens` | integer | `1024` | Maximum tokens in response |
| `topP` | float | `0.95` | Nucleus sampling parameter |
| `topK` | integer | `40` | Top-k sampling parameter |

### imageConfig

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `aspectRatio` | string | `1:1`, `3:4`, `4:3`, `9:16`, `16:9` | Output image aspect ratio |
| `personGeneration` | string | `DONT_ALLOW`, `ALLOW_ADULT`, `ALLOW_ALL` | Person generation policy |

### safetySettings

```json
{
  "safetySettings": [
    {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
  ]
}
```

**Threshold Options:**
- `BLOCK_NONE`
- `BLOCK_ONLY_HIGH`
- `BLOCK_MEDIUM_AND_ABOVE`
- `BLOCK_LOW_AND_ABOVE`

## Pricing

### Pay-As-You-Go (Gemini API)

**Image Generation:**
- 4K images: **$0.24** per image
- 2K images: **$0.134** per image
- 1K images: **$0.134** per image

**Image Inputs:**
- Per image: **$0.0011**

### Gemini 3 Pro (Text + Image Output)

Per 1M tokens:

| Context Size | Input | Output (Text) | Output (Image) |
|--------------|-------|---------------|----------------|
| ≤ 200k tokens | $2.00 | $12.00 | $120.00 |
| > 200k tokens | $4.00 | $18.00 | N/A |

### Subscription Plans

- **Google AI Plus**: $19.99/month (higher quota)
- **Google AI Pro**: $19.99/month
- **Google AI Ultra**: $249.99/month (watermark removal, highest limits)

### Free Tier

Google AI Studio offers free tier with rate limits:
- Limited daily quota
- Restricted to smaller images
- Rate: ~100 requests per day

## Rate Limits

### Free Tier

- **Requests per day**: ~100
- **Requests per minute**: 2-5
- **Concurrent requests**: 1

### Paid Tier

- **Requests per day**: Unlimited (subject to quota)
- **Requests per minute**: 60
- **Concurrent requests**: 10

### Vertex AI (Enterprise)

- **Custom quotas** available
- **Provisioned throughput** options
- **SLA guarantees**

## Best Practices

### Error Handling

Always implement retry logic with exponential backoff:

```python
import time

max_retries = 3
retry_delay = 1

for attempt in range(max_retries):
    try:
        response = make_api_request()
        break
    except RateLimitError:
        if attempt < max_retries - 1:
            time.sleep(retry_delay * (2 ** attempt))
        else:
            raise
```

### Request Optimization

1. **Batch similar requests** when possible
2. **Cache responses** for identical prompts
3. **Use lower resolutions** for drafts, 4K for finals
4. **Implement request queuing** for high-volume applications

### Image Size Management

- **1K** for quick iterations and previews
- **2K** for balanced quality (recommended default)
- **4K** for final production output only

### Timeout Configuration

Recommended timeouts:
- **Generation**: 60 seconds
- **Editing**: 90 seconds (more complex)
- **Multiple images**: 120 seconds

## cURL Examples

### Basic Generation

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -X POST \
  -d '{
    "contents": [{
      "parts": [{"text": "A futuristic cityscape at sunset"}]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "temperature": 0.7,
      "maxOutputTokens": 1024,
      "imageConfig": {
        "aspectRatio": "16:9"
      }
    }
  }'
```

### Image Editing

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -X POST \
  -d "{
    \"contents\": [{
      \"parts\": [
        {\"text\": \"Make the sky blue\"},
        {
          \"inlineData\": {
            \"mimeType\": \"image/jpeg\",
            \"data\": \"$(base64 -i input.jpg)\"
          }
        }
      ]
    }],
    \"generationConfig\": {
      \"responseModalities\": [\"TEXT\", \"IMAGE\"]
    }
  }"
```

## Python SDK Example

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

# Generate image
response = client.models.generate_images(
    model='gemini-3-pro-image-preview',
    prompt='A beautiful mountain landscape',
    config={
        'number_of_images': 1,
        'aspect_ratio': '16:9',
        'output_mime_type': 'image/jpeg'
    }
)

# Save image
for img in response.generated_images:
    with open('output.jpg', 'wb') as f:
        f.write(img.image.image_bytes)
```

## JavaScript/Node.js SDK Example

```javascript
import { GoogleGenAI } from "@google/genai";

const genAI = new GoogleGenAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({
  model: "gemini-3-pro-image-preview"
});

const result = await model.generateContent([
  "A serene lake at sunrise"
]);

const response = await result.response;
console.log(response.text());
```

## Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check billing/permissions |
| 404 | Not Found | Verify model name |
| 429 | Rate Limited | Implement backoff |
| 500 | Server Error | Retry with backoff |
| 503 | Service Unavailable | Retry later |

## Additional Resources

- **Official Documentation**: https://ai.google.dev/gemini-api/docs
- **Google AI Studio**: https://aistudio.google.com
- **Vertex AI Console**: https://console.cloud.google.com/vertex-ai
- **Pricing Details**: https://ai.google.dev/gemini-api/docs/pricing
- **Model Page**: https://deepmind.google/models/gemini-image/pro/
