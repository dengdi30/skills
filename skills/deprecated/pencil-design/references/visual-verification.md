# Visual Verification

> Workflow step: **V2-2 / V2-4. Visual Verification**

Covers screenshot capture and layout problem detection for design verification.

## Core Principle

**Never skip visual verification.** Every section built must be verified with both:

1. `pencil_get_screenshot` — visual check
2. `pencil_snapshot_layout` — structural problem check

## When to Verify

| Trigger | Action |
|---------|--------|
| After inserting any element | Verify the parent frame |
| After building a complete section | Screenshot the section |
| After building a complete screen | Screenshot the screen |
| After any structural change | Layout check the affected area |
| Before design review (V2-4) | Screenshot all screens at all breakpoints |

## Screenshot Capture

### Capture a Single Node

```javascript
pencil_get_screenshot({
  filePath: "path/to/file.pen",
  nodeId: "sectionId"
})
```

### Capture Multiple Nodes

```javascript
pencil_get_screenshot({
  filePath: "path/to/file.pen",
  nodeIds: ["section1Id", "section2Id", "section3Id"]
})
```

### What to Look For

- Text overflow or clipping
- Misaligned elements
- Inconsistent spacing
- Broken layout
- Color or contrast issues
- Missing content
- Overlapping elements

## Layout Problem Detection

### Check for Problems

```javascript
pencil_snapshot_layout({
  filePath: "path/to/file.pen",
  parentId: "screenId",
  maxDepth: 3,
  problemsOnly: true
})
```

Returns layout problems:

```json
{
  "problems": [
    {
      "type": "overflow",
      "nodeId": "titleText",
      "description": "Text content is clipped by parent frame",
      "severity": "high"
    },
    {
      "type": "clipping",
      "nodeId": "cardContent",
      "description": "Child element extends beyond parent bounds",
      "severity": "high"
    },
    {
      "type": "overlap",
      "nodeId": "button1",
      "description": "Overlaps with adjacent element",
      "severity": "medium"
    }
  ]
}
```

### Problem Types

| Problem Type | Severity | Fix |
|-------------|----------|-----|
| `overflow` | high | Set text `width: "fill_container"` or reduce content |
| `clipping` | high | Constrain child to parent bounds |
| `overlap` | medium | Add auto-layout to parent or increase gap |
| `alignment` | medium | Use `alignItems` / `justifyContent` |

### Full Layout Snapshot (Without Filter)

```javascript
pencil_snapshot_layout({
  filePath: "path/to/file.pen",
  parentId: "screenId",
  maxDepth: 5
})
```

Returns full layout tree. Useful for understanding structure when problems are subtle.

## Verification Workflow

### Per-Section Verification

After building each section:

```javascript
// 1. Screenshot the section
pencil_get_screenshot({
  filePath: "path/to/file.pen",
  nodeId: "sectionId"
})

// 2. Check for layout problems
pencil_snapshot_layout({
  filePath: "path/to/file.pen",
  parentId: "sectionId",
  maxDepth: 3,
  problemsOnly: true
})

// 3. If problems exist, fix them
// 4. Re-verify
```

### Per-Screen Verification

After building a complete screen:

```javascript
// 1. Screenshot the full screen
pencil_get_screenshot({
  filePath: "path/to/file.pen",
  nodeId: "screenId"
})

// 2. Full layout check
pencil_snapshot_layout({
  filePath: "path/to/file.pen",
  parentId: "screenId",
  maxDepth: 5,
  problemsOnly: true
})

// 3. Fix any remaining issues
```

### Pre-Review Verification (V2-4)

Before design review:

1. For each screen:
   - Screenshot at mobile (375px)
   - Screenshot at desktop (1280px)
   - Run layout check at both breakpoints
2. Save all screenshots to `screenshots/.tmp/`
3. Run final layout check on all screens
4. Save layout report to `screenshots/layout-report.md`
5. Promote approved screenshots from `.tmp/` to `screenshots/`

## Screenshot Storage

### During Work

Screenshots captured during design work go to a temporary location:

```
docs/designs/<feature>/screenshots/.tmp/
├── section-1-iteration-1.png
├── section-1-iteration-2.png
├── section-2-iteration-1.png
└── ...
```

### After Approval

Approved screenshots are promoted:

```
docs/designs/<feature>/screenshots/
├── mobile-home-default.png
├── mobile-home-hover.png
├── desktop-home-default.png
├── desktop-home-hover.png
└── layout-report.md
```

### Git Rules

- `.tmp/` is gitignored
- Only approved screenshots in `screenshots/` are committed
- `layout-report.md` is committed

## Common Visual Issues

| Issue | How to Detect | Fix |
|-------|---------------|-----|
| Text clipping | Layout check + screenshot | `width: "fill_container"` + `maxLines` |
| Misaligned items | Screenshot visual check | Use `alignItems: "center"` |
| Inconsistent spacing | Screenshot visual check | Use consistent `gap` values |
| Color mismatch | Screenshot visual check | Verify variable reference |
| Empty space at bottom | Layout check | Use `height: "fill_container"` for filler |
| Element overlapping | Layout check | Add auto-layout to parent |

## Verification Checklist

After every section:

- [ ] Screenshot captured?
- [ ] Layout check run with `problemsOnly: true`?
- [ ] All `high` severity problems fixed?
- [ ] All `medium` severity problems reviewed?
- [ ] Screenshot re-captured after fixes?

Before design review:

- [ ] Screenshots at all breakpoints captured?
- [ ] All screenshots promoted from `.tmp/` to `screenshots/`?
- [ ] Layout report saved to `screenshots/layout-report.md`?
- [ ] No remaining `high` severity layout problems?

## See Also

- [wireframe-and-layout.md](wireframe-and-layout.md) — Layout construction and overflow prevention
- [component-specification.md](component-specification.md) — Component contract template
