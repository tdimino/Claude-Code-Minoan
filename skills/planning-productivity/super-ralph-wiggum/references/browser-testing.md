# Browser Testing with Dev-Browser Skill

For UI changes in Ralph loops, verify with screenshots using the dev-browser skill.

## Quick Setup

```
Load the dev-browser skill
```

Then start the browser server:

```bash
# Start the browser server
~/.config/amp/skills/dev-browser/server.sh &
# Wait for "Ready" message
```

## Taking Screenshots

Use TypeScript/Node.js scripts with Playwright:

```bash
cd ~/.config/amp/skills/dev-browser && npx tsx <<'EOF'
import { connect, waitForPageLoad } from "@/client.js";

const client = await connect();
const page = await client.page("test");

// Set viewport
await page.setViewportSize({ width: 1280, height: 900 });

// Navigate to your app
const port = process.env.PORT || "3000";
await page.goto(`http://localhost:${port}/your-page`);
await waitForPageLoad(page);

// Take screenshot
await page.screenshot({ path: "tmp/screenshot.png" });

await client.disconnect();
EOF
```

## Common Verification Patterns

### Verify Page Load

```typescript
await page.goto("http://localhost:3000/login");
await waitForPageLoad(page);
await page.screenshot({ path: "tmp/login-page.png" });
```

### Verify Form Submission

```typescript
// Fill form
await page.fill('[name="email"]', 'test@example.com');
await page.fill('[name="password"]', 'password123');
await page.click('button[type="submit"]');

// Wait for navigation
await waitForPageLoad(page);
await page.screenshot({ path: "tmp/after-submit.png" });
```

### Verify Error States

```typescript
// Trigger error
await page.fill('[name="email"]', 'invalid-email');
await page.click('button[type="submit"]');

// Wait for error message
await page.waitForSelector('.error-message');
await page.screenshot({ path: "tmp/error-state.png" });
```

### Verify Responsive Layout

```typescript
// Mobile viewport
await page.setViewportSize({ width: 375, height: 667 });
await page.screenshot({ path: "tmp/mobile.png" });

// Tablet viewport
await page.setViewportSize({ width: 768, height: 1024 });
await page.screenshot({ path: "tmp/tablet.png" });

// Desktop viewport
await page.setViewportSize({ width: 1920, height: 1080 });
await page.screenshot({ path: "tmp/desktop.png" });
```

## Integration with Ralph Templates

When using `--browser` flag with Ralph templates, the system adds:

```
BROWSER TESTING:
For UI changes, verify with screenshots using the dev-browser skill.
Load the skill with: Load the dev-browser skill
Take screenshots to verify visual changes are correct.
Do NOT mark UI features complete without visual verification.
```

### In test-coverage Template

Verify UI component tests with screenshots:

```typescript
// After writing component test
await page.goto("http://localhost:3000/storybook/button");
await page.screenshot({ path: "tmp/button-component.png" });
// Verify button renders correctly
```

### In feature-prd Template

Verify each UI feature before marking `passes: true`:

```typescript
// Acceptance criteria: "Login button visible on homepage"
await page.goto("http://localhost:3000");
const loginButton = await page.locator('button:has-text("Login")');
expect(await loginButton.isVisible()).toBe(true);
await page.screenshot({ path: "tmp/feature-1-verified.png" });
```

## Best Practices

### 1. Screenshot Naming

Use descriptive names that include context:

```
tmp/iteration-5-login-form.png
tmp/feature-US001-complete.png
tmp/error-invalid-email.png
```

### 2. Before/After Comparisons

Take screenshots before and after changes:

```typescript
// Before
await page.screenshot({ path: "tmp/before-change.png" });

// Make changes...

// After
await page.screenshot({ path: "tmp/after-change.png" });
```

### 3. Full Page vs Viewport

```typescript
// Viewport only (faster, smaller files)
await page.screenshot({ path: "tmp/viewport.png" });

// Full page scroll capture
await page.screenshot({ path: "tmp/full-page.png", fullPage: true });
```

### 4. Element-Specific Screenshots

```typescript
// Screenshot specific element
const button = await page.locator('.submit-button');
await button.screenshot({ path: "tmp/button-only.png" });
```

## Troubleshooting

### Server Not Starting

```bash
# Check if port is in use
lsof -i :3000

# Kill existing process
kill -9 $(lsof -t -i :3000)

# Restart server
~/.config/amp/skills/dev-browser/server.sh &
```

### Screenshots Blank

- Ensure dev server is running (`npm run dev`)
- Check URL is correct
- Add `await waitForPageLoad(page)` after navigation

### Timeouts

```typescript
// Increase timeout for slow pages
await page.goto("http://localhost:3000", { timeout: 30000 });
```

## Cleanup

After verification:

```bash
# Remove temporary screenshots
rm -rf tmp/*.png
```

Or keep for debugging and include in progress log.
