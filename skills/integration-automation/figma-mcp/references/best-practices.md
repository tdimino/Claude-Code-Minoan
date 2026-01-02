# Figma MCP Best Practices

Extended best practices, detailed examples, and advanced patterns for design-to-code conversion using Figma MCP server.

## Design-to-Code Accuracy

### Exact Value Preservation

**Principle:** Never approximate measurements, colors, or spacing. Use exact values from Figma data.

**Why:** Approximation compounds across elements, leading to layouts that "feel off" even if visually close.

**Example:**

```typescript
// ❌ BAD - Approximated values
const spacing = {
  small: '8px',    // Figma shows 7px
  medium: '16px',  // Figma shows 14px
  large: '24px'    // Figma shows 26px
};

// ✅ GOOD - Exact Figma values
const spacing = {
  small: '7px',
  medium: '14px',
  large: '26px'
};
```

### Color Accuracy

**Principle:** Extract exact hex/rgba values from Figma, including opacity.

**Example from Figma data:**

```json
{
  "fills": [{
    "type": "SOLID",
    "color": {
      "r": 0.2,
      "g": 0.4,
      "b": 0.8
    },
    "opacity": 0.9
  }]
}
```

**Convert to CSS:**

```css
/* Calculate hex from RGB (r*255, g*255, b*255) */
/* r: 0.2 * 255 = 51 (0x33) */
/* g: 0.4 * 255 = 102 (0x66) */
/* b: 0.8 * 255 = 204 (0xCC) */

.element {
  background-color: #3366CC;
  opacity: 0.9;
}

/* Or use rgba for single property */
.element {
  background-color: rgba(51, 102, 204, 0.9);
}
```

### Auto-Layout to Flexbox Mapping

Figma's auto-layout directly maps to CSS Flexbox. Preserve the exact behavior.

**Figma Auto-Layout Properties → CSS:**

| Figma Property | CSS Equivalent |
|----------------|----------------|
| Direction: Horizontal | `flex-direction: row` |
| Direction: Vertical | `flex-direction: column` |
| Spacing: 12 | `gap: 12px` |
| Padding: 16, 24, 16, 24 | `padding: 16px 24px` |
| Alignment: Center | `align-items: center` |
| Justify: Space Between | `justify-content: space-between` |
| Hug Contents | `width: fit-content` or don't set width |
| Fill Container | `flex: 1` or `width: 100%` |

**Example:**

```json
// Figma auto-layout data
{
  "layoutMode": "HORIZONTAL",
  "primaryAxisAlignItems": "SPACE_BETWEEN",
  "counterAxisAlignItems": "CENTER",
  "itemSpacing": 12,
  "paddingLeft": 16,
  "paddingRight": 16,
  "paddingTop": 8,
  "paddingBottom": 8
}
```

```css
/* Generated CSS */
.container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
}
```

### Typography Precision

Extract complete typography properties from Figma text styles.

**Figma Typography Data:**

```json
{
  "fontFamily": "Inter",
  "fontWeight": 600,
  "fontSize": 16,
  "lineHeightPx": 24,
  "letterSpacing": -0.5,
  "textCase": "UPPER"
}
```

**Generated CSS:**

```css
.text-style {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 16px;
  line-height: 24px;  /* 1.5 ratio */
  letter-spacing: -0.5px;
  text-transform: uppercase;
}
```

## Component Architecture

### Identifying Reusable Components

**Pattern Recognition:**

1. **Figma Components** → Always become code components
2. **Repeated Structures** → Extract into components even if not Figma components
3. **Instance Variants** → Props or conditional rendering

**Example: Button Component**

Figma structure:
```
Button [Component]
├── Variant: Type (Primary, Secondary, Tertiary)
├── Variant: Size (Small, Medium, Large)
└── Variant: State (Default, Hover, Disabled)
```

Generated React component:

```typescript
// Button.tsx
interface ButtonProps {
  type?: 'primary' | 'secondary' | 'tertiary';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({
  type = 'primary',
  size = 'medium',
  disabled = false,
  children,
  onClick
}) => {
  return (
    <button
      className={`btn btn--${type} btn--${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
```

```css
/* Button.css */
.btn {
  /* Base styles from Figma */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

/* Size variants */
.btn--small {
  padding: 8px 16px;
  font-size: 14px;
  line-height: 20px;
}

.btn--medium {
  padding: 12px 24px;
  font-size: 16px;
  line-height: 24px;
}

.btn--large {
  padding: 16px 32px;
  font-size: 18px;
  line-height: 28px;
}

/* Type variants */
.btn--primary {
  background-color: #3366CC;
  color: #FFFFFF;
}

.btn--primary:hover {
  background-color: #2952A3;
}

.btn--secondary {
  background-color: #FFFFFF;
  color: #3366CC;
  border: 2px solid #3366CC;
}

.btn--tertiary {
  background-color: transparent;
  color: #3366CC;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
```

### Component Naming Conventions

**Principle:** Match Figma component names to code component names for consistency.

**Mapping:**

| Figma Name | Code Name (React) | Code Name (CSS) |
|------------|-------------------|-----------------|
| `Button/Primary` | `Button` (with props) | `.btn--primary` |
| `Card/Default` | `Card` | `.card` |
| `Input/Text Field` | `TextField` | `.text-field` |
| `Navigation/Header` | `Header` | `.header` |

**Example:**

```
Figma: "Card/Product"
React: <ProductCard />
CSS: .product-card
```

## Design System Integration

### Extracting Design Tokens

**Use Figma Variables** for design system tokens. These map directly to CSS custom properties.

**Figma Variables Data:**

```json
{
  "variables": {
    "color": {
      "primary": "#3366CC",
      "secondary": "#66CC33",
      "neutral-100": "#F5F5F5",
      "neutral-900": "#1A1A1A"
    },
    "spacing": {
      "xs": "4px",
      "sm": "8px",
      "md": "16px",
      "lg": "24px",
      "xl": "32px"
    },
    "typography": {
      "font-size-sm": "14px",
      "font-size-md": "16px",
      "font-size-lg": "20px",
      "line-height-sm": "20px",
      "line-height-md": "24px",
      "line-height-lg": "28px"
    }
  }
}
```

**Generated CSS Custom Properties:**

```css
:root {
  /* Colors */
  --color-primary: #3366CC;
  --color-secondary: #66CC33;
  --color-neutral-100: #F5F5F5;
  --color-neutral-900: #1A1A1A;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* Typography */
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 20px;
  --line-height-sm: 20px;
  --line-height-md: 24px;
  --line-height-lg: 28px;
}
```

**Usage in Components:**

```css
.button {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--color-primary);
  font-size: var(--font-size-md);
  line-height: var(--line-height-md);
}
```

### Theme Configuration (JavaScript/TypeScript)

For React/Vue projects with theme objects:

```typescript
// theme.ts
export const theme = {
  colors: {
    primary: '#3366CC',
    secondary: '#66CC33',
    neutral: {
      100: '#F5F5F5',
      900: '#1A1A1A'
    }
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px'
  },
  typography: {
    fontSize: {
      sm: '14px',
      md: '16px',
      lg: '20px'
    },
    lineHeight: {
      sm: '20px',
      md: '24px',
      lg: '28px'
    }
  }
} as const;

export type Theme = typeof theme;
```

## Responsive Design

### Constraint Mapping

Figma constraints determine how elements respond to container size changes.

**Figma Constraints → CSS:**

| Figma Constraint | CSS Equivalent |
|------------------|----------------|
| Left + Right | `width: 100%` or `left: 0; right: 0;` |
| Top + Bottom | `height: 100%` or `top: 0; bottom: 0;` |
| Left + Width | `width: [fixed]px; margin-right: auto;` |
| Right + Width | `width: [fixed]px; margin-left: auto;` |
| Center (H) | `margin: 0 auto;` |
| Center (V) | `margin: auto 0;` |
| Scale | `width: [%]; height: [%];` |

**Example:**

```json
// Figma constraints
{
  "constraints": {
    "horizontal": "LEFT_RIGHT",  // Stretch horizontally
    "vertical": "TOP"            // Fixed to top
  }
}
```

```css
.element {
  width: 100%;
  /* Or */
  left: 0;
  right: 0;
  top: 0;
}
```

### Breakpoint Strategy

When Figma has desktop and mobile variants:

```css
/* Desktop-first approach */
.container {
  /* Desktop styles (from Figma desktop frame) */
  padding: 48px;
  flex-direction: row;
  gap: 24px;
}

@media (max-width: 768px) {
  .container {
    /* Mobile styles (from Figma mobile frame) */
    padding: 16px;
    flex-direction: column;
    gap: 16px;
  }
}
```

### Fluid Typography

When Figma shows different font sizes for breakpoints:

```css
.heading {
  /* Desktop: 48px */
  font-size: 48px;
  line-height: 56px;
}

@media (max-width: 768px) {
  .heading {
    /* Mobile: 32px */
    font-size: 32px;
    line-height: 40px;
  }
}

/* Or use clamp for fluid scaling */
.heading {
  font-size: clamp(32px, 4vw, 48px);
  line-height: clamp(40px, 5vw, 56px);
}
```

## Code Quality

### Semantic HTML

**Principle:** Use appropriate HTML elements based on content meaning, not just visual appearance.

**Mapping Visual Patterns to Semantic HTML:**

| Visual Pattern | Semantic HTML |
|----------------|---------------|
| Page title | `<h1>` |
| Section headings | `<h2>`, `<h3>`, etc. |
| Navigation bar | `<nav>` with `<ul>` and `<li>` |
| Main content area | `<main>` |
| Article/blog post | `<article>` |
| Sidebar content | `<aside>` |
| Footer | `<footer>` |
| Call-to-action | `<button>` or `<a>` |
| Form inputs | `<input>`, `<select>`, `<textarea>` |
| Lists | `<ul>`, `<ol>`, `<li>` |
| Metadata/supplementary | `<small>`, `<time>`, `<address>` |

**Example: Converting Figma Frame Structure**

Figma structure:
```
Landing Page
├── Header Frame
│   ├── Logo (Image)
│   └── Nav Links (Text x5)
├── Hero Frame
│   ├── Headline (Text)
│   ├── Subheading (Text)
│   └── CTA Button (Rectangle + Text)
├── Features Frame
│   ├── Feature 1 (Group)
│   ├── Feature 2 (Group)
│   └── Feature 3 (Group)
└── Footer Frame
    ├── Copyright (Text)
    └── Social Links (Icons)
```

Semantic HTML:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Landing Page</title>
</head>
<body>
  <header>
    <img src="logo.svg" alt="Company Logo">
    <nav>
      <ul>
        <li><a href="#features">Features</a></li>
        <li><a href="#pricing">Pricing</a></li>
        <li><a href="#about">About</a></li>
        <li><a href="#blog">Blog</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main>
    <section class="hero">
      <h1>Headline Text</h1>
      <p>Subheading text</p>
      <button>Get Started</button>
    </section>

    <section class="features">
      <article>Feature 1 content</article>
      <article>Feature 2 content</article>
      <article>Feature 3 content</article>
    </section>
  </main>

  <footer>
    <p>&copy; 2025 Company Name</p>
    <nav aria-label="Social media">
      <ul>
        <li><a href="#">Twitter</a></li>
        <li><a href="#">LinkedIn</a></li>
      </ul>
    </nav>
  </footer>
</body>
</html>
```

### Accessibility (ARIA)

Add accessibility attributes for interactive elements and dynamic content.

**Essential ARIA Patterns:**

```html
<!-- Buttons with icons only -->
<button aria-label="Close menu">
  <svg><!-- icon --></svg>
</button>

<!-- Navigation landmark -->
<nav aria-label="Main navigation">
  <ul><!-- nav items --></ul>
</nav>

<!-- Form inputs with labels -->
<label for="email">Email Address</label>
<input
  type="email"
  id="email"
  name="email"
  aria-required="true"
  aria-describedby="email-error"
>
<span id="email-error" role="alert"><!-- Error message --></span>

<!-- Tab interface -->
<div role="tablist" aria-label="Content tabs">
  <button role="tab" aria-selected="true" aria-controls="panel1">Tab 1</button>
  <button role="tab" aria-selected="false" aria-controls="panel2">Tab 2</button>
</div>
<div role="tabpanel" id="panel1">Content 1</div>
<div role="tabpanel" id="panel2" hidden>Content 2</div>

<!-- Modal dialog -->
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
>
  <h2 id="dialog-title">Dialog Title</h2>
  <p id="dialog-description">Dialog content</p>
  <button>Close</button>
</div>
```

## Performance Optimization

### Image Optimization

**Figma Image Exports → Optimized Web Images:**

| Image Type | Export Format | Optimization |
|------------|---------------|--------------|
| Icons (solid colors) | SVG | Inline SVG or SVG sprite |
| Photos | WebP + JPG fallback | Compression, responsive sizes |
| Illustrations | SVG or WebP | Optimize SVG paths, compress |
| Background patterns | SVG or CSS | CSS patterns if possible |

**Responsive Images:**

```html
<!-- For photos/raster images -->
<picture>
  <source
    srcset="image-large.webp 1200w, image-medium.webp 800w, image-small.webp 400w"
    type="image/webp"
  >
  <source
    srcset="image-large.jpg 1200w, image-medium.jpg 800w, image-small.jpg 400w"
    type="image/jpeg"
  >
  <img
    src="image-medium.jpg"
    alt="Description"
    loading="lazy"
    width="800"
    height="600"
  >
</picture>
```

### CSS Efficiency

**Avoid redundancy:**

```css
/* ❌ BAD - Repeated styles */
.card-1 {
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-2 {
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* ✅ GOOD - Shared base class */
.card {
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card--variant-1 { /* variant-specific styles */ }
.card--variant-2 { /* variant-specific styles */ }
```

**Use CSS custom properties for reusability:**

```css
:root {
  --card-padding: 16px;
  --card-radius: 8px;
  --card-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card {
  padding: var(--card-padding);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}
```

## Advanced Patterns

### Complex Auto-Layout Scenarios

**Nested Auto-Layouts:**

Figma:
```
Container (Horizontal, Gap: 24)
├── Sidebar (Vertical, Gap: 16, Width: 240px)
│   ├── Item 1
│   └── Item 2
└── Main Content (Vertical, Gap: 32, Fill)
    ├── Section 1
    └── Section 2
```

CSS:

```css
.container {
  display: flex;
  flex-direction: row;
  gap: 24px;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 240px;
  flex-shrink: 0;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
  flex: 1;
}
```

### Grid Layouts

When Figma shows a grid-like structure:

```css
/* Regular grid */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

/* Responsive grid */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}
```

### Animation and Transitions

Figma prototypes with transitions → CSS transitions/animations:

```css
/* Hover transitions from Figma prototype */
.button {
  background-color: #3366CC;
  transition: background-color 0.2s ease;
}

.button:hover {
  background-color: #2952A3;
}

/* Smart Animate → CSS animation */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  animation: fadeInUp 0.4s ease;
}
```

## Workflow Optimizations

### Batch Processing

When implementing multiple screens/components:

1. **Fetch all design data upfront**
2. **Identify shared patterns** (repeated components, styles)
3. **Extract design tokens first**
4. **Build base components**
5. **Compose page layouts**

### Design System First Approach

If the Figma file has variables and components:

1. **Extract design tokens** (`get_figma_variables`)
2. **Generate theme configuration**
3. **Implement base components** (buttons, inputs, cards)
4. **Build composite components**
5. **Assemble pages**

This ensures consistency and reduces code duplication.

### Iterative Refinement

Don't aim for perfection in first pass:

**Pass 1: Structure**
- Layout hierarchy
- Spacing and sizing
- Basic styling

**Pass 2: Refinement**
- Extract design tokens
- Componentize repeated patterns
- Add responsive behavior

**Pass 3: Polish**
- Accessibility
- Animations/transitions
- Performance optimization

## Common Pitfalls to Avoid

### ❌ Over-Divs

Don't create nested divs unnecessarily:

```html
<!-- BAD -->
<div class="container">
  <div class="wrapper">
    <div class="inner">
      <div class="content">
        <h1>Title</h1>
      </div>
    </div>
  </div>
</div>

<!-- GOOD -->
<section class="container">
  <h1>Title</h1>
</section>
```

### ❌ Absolute Positioning Overuse

Figma allows absolute positioning anywhere, but in code it's fragile:

```css
/* AVOID unless necessary */
.element {
  position: absolute;
  top: 47px;
  left: 123px;
}

/* PREFER relative layouts */
.container {
  display: flex;
  padding: 47px 0 0 123px;
}
```

### ❌ Pixel-Perfect Obsession at Wrong Level

Match design at component level, not individual pixel positions:

- ✅ Spacing between elements
- ✅ Component dimensions
- ✅ Typography sizes
- ❌ Absolute X/Y coordinates (unless truly needed)

### ❌ Ignoring Mobile Variants

If Figma has mobile designs, implement them:

```css
/* DON'T ignore mobile */
.container {
  padding: 48px; /* Desktop only */
}

/* DO provide mobile styles */
.container {
  padding: 48px;
}

@media (max-width: 768px) {
  .container {
    padding: 16px;
  }
}
```

## Summary Checklist

When implementing a Figma design:

- [ ] Fetch complete design data via MCP
- [ ] Extract design tokens (colors, spacing, typography)
- [ ] Map Figma components to code components
- [ ] Preserve exact values (no approximation)
- [ ] Use semantic HTML
- [ ] Map auto-layout to Flexbox correctly
- [ ] Implement responsive behavior from constraints
- [ ] Add accessibility attributes
- [ ] Optimize images
- [ ] Test across breakpoints
- [ ] Validate against original design
