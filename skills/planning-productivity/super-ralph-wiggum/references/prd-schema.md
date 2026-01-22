# PRD Schema for Ralph Wiggum Loops

The PRD (Product Requirements Document) approach is Matt Pocock's recommended method for scoping Ralph loops. It prevents context rot and ensures focused iteration.

## Why PRD-Based Loops?

Two problems emerge with naive Ralph loops:

1. **Scope Creep**: Agent picks tasks that are too large
2. **No Stopping Point**: Agent doesn't know when to stop

The PRD approach solves both by:
- Breaking work into small, atomic user stories
- Providing explicit pass/fail tracking
- Enforcing priority ordering

## Basic PRD Schema

```json
{
  "name": "Project Name",
  "description": "Brief project description",
  "features": [
    {
      "id": 1,
      "story": "User can create an account with email",
      "passes": false,
      "priority": 1
    },
    {
      "id": 2,
      "story": "User can log in with email and password",
      "passes": false,
      "priority": 2
    }
  ]
}
```

## Extended PRD Schema

For complex projects, use the extended schema:

```json
{
  "name": "E-commerce Checkout",
  "version": "1.0.0",
  "description": "Complete checkout flow implementation",

  "metadata": {
    "created": "2024-01-15",
    "updated": "2024-01-15",
    "author": "team@example.com"
  },

  "features": [
    {
      "id": 1,
      "story": "User can add items to cart",
      "passes": false,
      "priority": 1,
      "acceptance_criteria": [
        "Cart icon shows item count",
        "Cart persists across page navigation",
        "Duplicate items increase quantity"
      ],
      "dependencies": [],
      "estimated_iterations": 2,
      "notes": ""
    },
    {
      "id": 2,
      "story": "User can view cart contents",
      "passes": false,
      "priority": 2,
      "acceptance_criteria": [
        "Shows item name, quantity, price",
        "Shows subtotal and total",
        "Can navigate to checkout"
      ],
      "dependencies": [1],
      "estimated_iterations": 1,
      "notes": ""
    },
    {
      "id": 3,
      "story": "User can update item quantity in cart",
      "passes": false,
      "priority": 3,
      "acceptance_criteria": [
        "Can increase/decrease quantity",
        "Can remove item (quantity 0)",
        "Total updates in real-time"
      ],
      "dependencies": [1, 2],
      "estimated_iterations": 1,
      "notes": ""
    }
  ],

  "verification": {
    "command": "pnpm test && pnpm build",
    "coverage_threshold": 80
  }
}
```

## Field Descriptions

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Project or feature group name |
| `features` | array | List of feature objects |
| `features[].id` | number | Unique identifier |
| `features[].story` | string | User story description |
| `features[].passes` | boolean | Whether feature is complete |
| `features[].priority` | number | Execution order (1 = highest) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Project description |
| `version` | string | PRD version |
| `metadata` | object | Creation/update info |
| `acceptance_criteria` | array | Specific requirements |
| `dependencies` | array | IDs of prerequisite features |
| `estimated_iterations` | number | Expected iterations |
| `notes` | string | Implementation notes |
| `verification` | object | Test/build commands |

## Using PRDs in Ralph Loops

### Prompt Template

```
@progress.txt @prd.json

Read prd.json and find the highest-priority feature where 'passes': false.

If all features have 'passes': true, output <promise>COMPLETE</promise>.

For the selected feature:
1. Read the story and acceptance_criteria
2. Check dependencies - all must pass first
3. Implement the feature
4. Verify against acceptance_criteria
5. Run verification command
6. Update prd.json to set 'passes': true
7. Commit and log progress

ONLY work on ONE feature per iteration.
```

### Handling Dependencies

```
When selecting a feature:
1. Find all features where 'passes': false
2. Filter to those whose dependencies all pass
3. Select the highest priority from filtered list
4. If no features available (blocked by deps):
   - Document the blocker
   - Skip this iteration
```

## PRD Templates by Project Type

### Web Application

```json
{
  "name": "User Dashboard",
  "features": [
    {"id": 1, "story": "User can view dashboard", "passes": false, "priority": 1},
    {"id": 2, "story": "Dashboard shows recent activity", "passes": false, "priority": 2},
    {"id": 3, "story": "User can customize dashboard layout", "passes": false, "priority": 3},
    {"id": 4, "story": "Dashboard data refreshes automatically", "passes": false, "priority": 4}
  ]
}
```

### API Development

```json
{
  "name": "REST API",
  "features": [
    {"id": 1, "story": "GET /users returns user list", "passes": false, "priority": 1},
    {"id": 2, "story": "POST /users creates new user", "passes": false, "priority": 2},
    {"id": 3, "story": "GET /users/:id returns single user", "passes": false, "priority": 3},
    {"id": 4, "story": "PUT /users/:id updates user", "passes": false, "priority": 4},
    {"id": 5, "story": "DELETE /users/:id removes user", "passes": false, "priority": 5}
  ]
}
```

### CLI Tool

```json
{
  "name": "CLI Tool",
  "features": [
    {"id": 1, "story": "User can run 'tool init' to create config", "passes": false, "priority": 1},
    {"id": 2, "story": "User can run 'tool build' to compile", "passes": false, "priority": 2},
    {"id": 3, "story": "User can run 'tool --help' for usage", "passes": false, "priority": 3},
    {"id": 4, "story": "Tool shows progress during long operations", "passes": false, "priority": 4}
  ]
}
```

### Documentation

```json
{
  "name": "API Documentation",
  "features": [
    {"id": 1, "story": "README has quick start guide", "passes": false, "priority": 1},
    {"id": 2, "story": "All public functions have JSDoc", "passes": false, "priority": 2},
    {"id": 3, "story": "API reference covers all endpoints", "passes": false, "priority": 3},
    {"id": 4, "story": "Examples show common use cases", "passes": false, "priority": 4}
  ]
}
```

## Best Practices

### 1. Keep Stories Small

❌ "User can manage their account"
✅ "User can update email address"
✅ "User can change password"
✅ "User can delete account"

### 2. Make Stories Testable

❌ "Dashboard looks good"
✅ "Dashboard shows user name in header"
✅ "Dashboard displays last 10 activities"

### 3. Order by Dependencies

Features with no dependencies should have higher priority so they're implemented first.

### 4. Update PRD Atomically

Each iteration should update exactly one feature's `passes` status.

### 5. Track Blockers in Notes

```json
{
  "id": 5,
  "story": "User can export data",
  "passes": false,
  "priority": 5,
  "notes": "Blocked: waiting for export API endpoint"
}
```
