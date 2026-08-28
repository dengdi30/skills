# Responsive Breakpoints

> Workflow step: **V2-3. High-Fidelity Design + Key Component Contracts**

Covers multi-artboard layout patterns for responsive design in Pencil.

## Tailwind v4 Default Breakpoints

| Prefix | Min Width | Typical Device |
|--------|-----------|----------------|
| (default) | 0px | Mobile portrait |
| `sm:` | 640px | Mobile landscape / small tablet |
| `md:` | 768px | Tablet portrait |
| `lg:` | 1024px | Tablet landscape / small laptop |
| `xl:` | 1280px | Desktop |
| `2xl:` | 1536px | Large desktop |

## Multi-Artboard Strategy

For every responsive design, create separate artboards:

```
Pencil Canvas
├── Mobile (375px)       # default styles
├── Tablet (768px)       # md: breakpoint overrides
├── Desktop (1280px)     # xl: breakpoint overrides
└── Wide (1536px)        # 2xl: breakpoint overrides (if needed)
```

### Common Mobile Widths

| Device | Width |
|--------|-------|
| iPhone SE | 375px |
| iPhone 14 | 390px |
| iPhone 14 Pro Max | 430px |
| Galaxy S22 | 360px |
| Pixel 7 | 412px |

Default to **375px** for the mobile artboard unless targeting a specific device.

### Common Desktop Widths

| Device | Width |
|--------|-------|
| Small laptop | 1280px |
| Standard desktop | 1440px |
| Wide desktop | 1536px |
| 4K | 1920px |

Default to **1280px** for the desktop artboard.

## Layout Patterns

### Pattern 1: Stack on Mobile, Grid on Desktop

Mobile:
```
[ Header ]
[ Card 1 ]
[ Card 2 ]
[ Card 3 ]
[ Footer ]
```

Desktop:
```
[ Header ]
[ Card 1 ][ Card 2 ][ Card 3 ]
[ Footer ]
```

Tailwind classes:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {cards.map(card => <Card key={card.id} {...card} />)}
</div>
```

### Pattern 2: Hidden Sidebar on Mobile

Mobile (sidebar hidden, hamburger menu):
```
[ Header (☰) ]
[ Main content ]
```

Desktop (sidebar visible):
```
[ Header        ]
[ Sidebar ][ Main content ]
```

Tailwind classes:

```tsx
<div className="flex">
  <Sidebar className="hidden md:block w-64" />
  <main className="flex-1 p-4">{children}</main>
</div>
```

### Pattern 3: Tab Navigation on Mobile

Mobile (tabs at top):
```
[ Tab 1 ][ Tab 2 ][ Tab 3 ]
[ Content for active tab ]
```

Desktop (sidebar nav):
```
[ Tab 1 ] [ Content         ]
[ Tab 2 ] [ for active tab  ]
[ Tab 3 ] [                  ]
```

### Pattern 4: Data Table Responsive

Mobile (cards instead of table):
```
[ Card 1 ]
[ Card 2 ]
[ Card 3 ]
```

Desktop (full table):
```
| Col 1 | Col 2 | Col 3 |
|-------|-------|-------|
| Data  | Data  | Data  |
```

Tailwind classes:

```tsx
{/* Desktop: table */}
<div className="hidden md:block">
  <Table>...</Table>
</div>

{/* Mobile: cards */}
<div className="md:hidden space-y-4">
  {items.map(item => <Card key={item.id}>...</Card>)}
</div>
```

## Touch Targets

For mobile designs, ensure all interactive elements meet minimum touch target size:

| Element | Min Size | Notes |
|---------|----------|-------|
| Button | 44x44px | Apple HIG / WCAG recommendation |
| Icon button | 44x44px | Use padding to expand touch area |
| Link | 44px height | Line-height or padding |
| Checkbox | 24x24px visual | Add padding to reach 44x44px |
| Radio button | 24x24px visual | Add padding to reach 44x44px |

In Tailwind v4:

```tsx
{/* Mobile touch target expansion */}
<button className="h-11 w-11 md:h-auto md:w-auto p-2 md:rounded-md">
  <Icon className="h-5 w-5" />
</button>
```

## Fluid Typography

Consider fluid typography for text that should scale smoothly between breakpoints:

```css
/* In tokens.css */
:root {
  --text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-lg: clamp(1.125rem, 1rem + 0.75vw, 1.25rem);
}
```

```tsx
<p className="text-base lg:text-lg">Fluid text</p>
```

## Container Widths

| Container | Max Width | Tailwind Class |
|-----------|-----------|----------------|
| Full width | none | `w-full` |
| Small container | 640px | `max-w-screen-sm` |
| Medium container | 768px | `max-w-screen-md` |
| Large container | 1024px | `max-w-screen-lg` |
| XL container | 1280px | `max-w-screen-xl` |
| 2XL container | 1536px | `max-w-screen-2xl` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Fixed width like `w-[375px]` | Use `w-full` with parent constraints |
| Fixed height like `h-[812px]` | Use `min-h-screen` or content-based height |
| Text overflowing container | Use `text-sm` or `truncate` |
| Sidebar always visible on mobile | Use `hidden md:block` |
| Table not responsive | Add card fallback with `md:hidden` / `hidden md:block` |
| Touch target too small | Add `p-2` or `min-h-[44px]` on mobile |

## Checklist

- [ ] Created separate artboards for mobile (375px) and desktop (1280px)?
- [ ] Used `grid-cols-1 md:grid-cols-N` for grid layouts?
- [ ] Used `hidden md:block` for desktop-only elements?
- [ ] Used `md:hidden` for mobile-only elements?
- [ ] All touch targets at least 44x44px on mobile?
- [ ] No fixed pixel widths from artboard dimensions?
- [ ] Documented breakpoint behavior in component spec?

## See Also

- [wireframe-and-layout.md](wireframe-and-layout.md) — Layout construction patterns
- [component-specification.md](component-specification.md) — Component contract template
- [design-to-code-workflow.md](design-to-code-workflow.md) — Code generation workflow
