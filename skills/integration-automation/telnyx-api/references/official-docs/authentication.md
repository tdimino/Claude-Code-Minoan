[Skip to main content](https://developers.telnyx.com/development/api-fundamentals/authentication#__docusaurus_skipToContent_fallback)

# Ask our

AI AssistantRead more [here](https://support.telnyx.com/en/articles/8020222-mission-control-portal-ai-chat-support).

Hello, how can I help you?

09:06

How do I set up a SIP trunk?

PoweredbyTelnyx

On this page

![Copy icon](https://developers.telnyx.com/img/icons/copy.svg)Copy for LLM![File text icon](https://developers.telnyx.com/img/icons/file-text.svg)View as Markdown

All Telnyx APIs use consistent authentication mechanisms to ensure secure access to your resources. This guide covers the universal authentication patterns used across Voice, Messaging, Cloud Storage, IoT, and all other Telnyx services.

## [API Keys ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#api-keys "Direct link to API Keys")

### [Overview ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#overview "Direct link to Overview")

Telnyx uses API Keys as the primary authentication method across all services. Your API Keys carry significant privileges and provide access to all Telnyx resources associated with your account.

### [Security Best Practices ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#security-best-practices "Direct link to Security Best Practices")

- **Keep API Keys secure**: Never share API Keys in publicly accessible areas such as GitHub, client-side code, or logs
- **Use environment variables**: Store API Keys in environment variables or secure configuration files
- **Rotate keys regularly**: Periodically generate new API Keys and deactivate old ones
- **Use least privilege**: If available, use API Keys with minimal required permissions

### [Managing API Keys ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#managing-api-keys "Direct link to Managing API Keys")

You can view and manage your API Keys in the Auth section of your [Mission Control portal](https://portal.telnyx.com/).

## [Authentication Methods ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#authentication-methods "Direct link to Authentication Methods")

### [Bearer Token Authentication ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#bearer-token-authentication "Direct link to Bearer Token Authentication")

Most Telnyx APIs use Bearer token authentication in the Authorization header:

```bash
curl -X GET \
  --header "Authorization: Bearer YOUR_API_KEY" \
  "https://api.telnyx.com/v2/endpoint"
```

### [SDK Authentication ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#sdk-authentication "Direct link to SDK Authentication")

When using Telnyx SDKs, authentication is typically configured once during initialization:

```javascript
// Node.js SDK
const telnyx = require('telnyx')('YOUR_API_KEY');

// Python SDK
import telnyx
telnyx.api_key = "YOUR_API_KEY"

// Ruby SDK
Telnyx.api_key = "YOUR_API_KEY"
```

## [Common Authentication Patterns ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#common-authentication-patterns "Direct link to Common Authentication Patterns")

### [RESTful APIs ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#restful-apis "Direct link to RESTful APIs")

- **Voice API**: Bearer token in Authorization header
- **Messaging API**: Bearer token in Authorization header
- **Cloud Storage**: AWS Signature Version 4 or Bearer token
- **IoT APIs**: Bearer token in Authorization header

### [Real-time Connections ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#real-time-connections "Direct link to Real-time Connections")

- **WebRTC**: JWT tokens for client authentication
- **WebSocket connections**: Bearer token during connection establishment

## [Error Handling ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#error-handling "Direct link to Error Handling")

### [Authentication Errors ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#authentication-errors "Direct link to Authentication Errors")

Common authentication-related HTTP status codes:

- **401 Unauthorized**: Invalid or missing API Key
- **403 Forbidden**: Valid API Key but insufficient permissions
- **429 Too Many Requests**: Rate limit exceeded

### [Debugging Authentication Issues ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#debugging-authentication-issues "Direct link to Debugging Authentication Issues")

1. **Verify API Key format**: Ensure the key is correctly formatted and complete
2. **Check headers**: Confirm the Authorization header is properly set
3. **Validate permissions**: Ensure your API Key has the required permissions for the resource
4. **Test with curl**: Use curl to isolate authentication issues from SDK problems

## [Environment-Specific Considerations ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#environment-specific-considerations "Direct link to Environment-Specific Considerations")

### [Development vs Production ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#development-vs-production "Direct link to Development vs Production")

- Use separate API Keys for development and production environments
- Never use production API Keys in development or testing
- Consider using restricted API Keys for development

### [Regional Considerations ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#regional-considerations "Direct link to Regional Considerations")

Some Telnyx services may have regional API endpoints. Always check the specific service documentation for the correct base URL.

## [Account Management ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#account-management "Direct link to Account Management")

### [Account Levels and Access ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#account-levels-and-access "Direct link to Account Levels and Access")

Account levels determine which APIs and features are available to you. For detailed information about account types, capabilities, and verification requirements, see [Account Levels and Capabilities](https://developers.telnyx.com/docs/account-setup/levels-and-capabilities).

## [Next Steps ​](https://developers.telnyx.com/development/api-fundamentals/authentication\#next-steps "Direct link to Next Steps")

- **API Reliability & Retries** \- Handle authentication failures gracefully
- **Webhook Security** \- Secure your webhook endpoints
- **SDKs & Tools** \- Language-specific authentication setup

On this page

- [API Keys ​](https://developers.telnyx.com/development/api-fundamentals/authentication#api-keys)
- [Authentication Methods ​](https://developers.telnyx.com/development/api-fundamentals/authentication#authentication-methods)
- [Common Authentication Patterns ​](https://developers.telnyx.com/development/api-fundamentals/authentication#common-authentication-patterns)
- [Error Handling ​](https://developers.telnyx.com/development/api-fundamentals/authentication#error-handling)
- [Environment-Specific Considerations ​](https://developers.telnyx.com/development/api-fundamentals/authentication#environment-specific-considerations)
- [Account Management ​](https://developers.telnyx.com/development/api-fundamentals/authentication#account-management)
- [Next Steps ​](https://developers.telnyx.com/development/api-fundamentals/authentication#next-steps)
