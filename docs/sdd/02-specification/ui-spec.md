# PerfWatch UI Specification

> User interface design and component specifications

---

## Design Principles

1. **Information Density** - Show as much data as possible without clutter
2. **Real-time Focus** - Live data is the primary experience
3. **Dark Theme** - Easier on eyes for extended monitoring
4. **Fixed Layout** - Consistent, predictable dashboard

---

## Color Palette

### Primary Colors (Dark Theme)
```css
--bg-primary: #0f172a;      /* Main background */
--bg-secondary: #1e293b;    /* Card background */
--bg-tertiary: #334155;     /* Hover states */
--text-primary: #f8fafc;    /* Main text */
--text-secondary: #94a3b8;  /* Secondary text */
--text-muted: #64748b;      /* Muted text */
--border: #334155;          /* Borders */
```

### Accent Colors
```css
--accent-blue: #3b82f6;     /* Primary actions */
--accent-green: #22c55e;    /* Success, good values */
--accent-yellow: #eab308;   /* Warning, medium values */
--accent-red: #ef4444;      /* Error, high values */
--accent-purple: #a855f7;   /* Highlights */
```

### Chart Colors
```css
--chart-1: #3b82f6;   /* Blue */
--chart-2: #22c55e;   /* Green */
--chart-3: #f59e0b;   /* Amber */
--chart-4: #ef4444;   /* Red */
--chart-5: #a855f7;   /* Purple */
--chart-6: #06b6d4;   /* Cyan */
--chart-7: #f97316;   /* Orange */
--chart-8: #ec4899;   /* Pink */
```

---

## Typography

```css
--font-family: 'Inter', -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

--text-xs: 0.75rem;    /* 12px - Labels */
--text-sm: 0.875rem;   /* 14px - Secondary */
--text-base: 1rem;     /* 16px - Body */
--text-lg: 1.125rem;   /* 18px - Headings */
--text-xl: 1.25rem;    /* 20px - Page titles */
--text-2xl: 1.5rem;    /* 24px - Dashboard title */
```

---

## Page Layouts

### Login Page (`/login`)

```
┌─────────────────────────────────────────────┐
│                                             │
│                                             │
│           ┌─────────────────┐               │
│           │   PerfWatch     │               │
│           │   [Logo]        │               │
│           ├─────────────────┤               │
│           │ Username        │               │
│           │ [____________]  │               │
│           │                 │               │
│           │ Password        │               │
│           │ [____________]  │               │
│           │                 │               │
│           │ [   Login    ]  │               │
│           │                 │               │
│           │ Error message   │               │
│           └─────────────────┘               │
│                                             │
│                                             │
└─────────────────────────────────────────────┘
```

**Components:**
- Centered card (max-width: 400px)
- Logo/title at top
- Username input
- Password input
- Login button (full width)
- Error message area (red text)

---

### Dashboard Page (`/`) - Main View

```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] PerfWatch              [Dashboard] [History] [⚙]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────┐ ┌─────────────────────────┐   │
│  │ CPU                     │ │ Memory                  │   │
│  │ ████████░░ 76%         │ │ ██████░░░░ 62%         │   │
│  │ [Chart: per-core usage] │ │ [Chart: usage breakdown]│   │
│  │                         │ │                         │   │
│  │ User: 52% Sys: 24%     │ │ Used: 10GB / 16GB      │   │
│  └─────────────────────────┘ └─────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────┐ ┌─────────────────────────┐   │
│  │ Network                 │ │ Disk I/O                │   │
│  │ ↑ 1.2 MB/s  ↓ 4.5 MB/s │ │ R: 52 MB/s W: 12 MB/s  │   │
│  │ [Chart: bandwidth]      │ │ [Chart: throughput]     │   │
│  │                         │ │                         │   │
│  │ eth0: 45 connections    │ │ sda: 150 IOPS          │   │
│  └─────────────────────────┘ └─────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────┐ ┌─────────────────────────┐   │
│  │ Cache Performance       │ │ Advanced CPU            │   │
│  │ [Chart: miss rates]     │ │ IPC: 1.85              │   │
│  │                         │ │ [Chart: cycles/instr]   │   │
│  │ L1: 1.2% L2: 8% L3: 25%│ │                         │   │
│  └─────────────────────────┘ └─────────────────────────┘   │
│                                                             │
│  Status: Connected • Last update: 2s ago                    │
└─────────────────────────────────────────────────────────────┘
```

**Layout:**
- Header: Logo, navigation, settings icon
- Grid: 2 columns, 3 rows of metric cards
- Footer: Connection status

**Metric Cards:**
- Title with icon
- Summary value (large)
- Chart area (ECharts)
- Detail values (small)

---

### History Page (`/history`)

```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] PerfWatch              [Dashboard] [History] [⚙]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Time Range: [▼ Last Hour ] [▼ CPU      ] [Compare ▼]      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │     Historical Chart                                │   │
│  │     (Large area chart)                              │   │
│  │                                                     │   │
│  │     [==========Line chart with time axis==========] │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────┐ ┌──────────────────────┐         │
│  │ Current Period       │ │ Comparison Period    │         │
│  │ Avg: 52%             │ │ Avg: 45%             │         │
│  │ Max: 98%             │ │ Max: 87%             │         │
│  │ Min: 12%             │ │ Min: 8%              │         │
│  └──────────────────────┘ └──────────────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Controls:**
- Time range selector (1h, 6h, 24h, 7d, 30d)
- Metric type selector (CPU, Memory, Network, Disk)
- Comparison toggle (None, Yesterday, Last Week)

**Charts:**
- Large historical chart with zoom capability
- Comparison overlay when enabled

---

### Settings Page (`/settings`)

```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] PerfWatch              [Dashboard] [History] [⚙]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Settings                                                   │
│  ─────────────────────────────────────────                  │
│                                                             │
│  Data Retention                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Keep data for: [30 ▼] days                          │   │
│  │ Downsample after: [7 ▼] days                        │   │
│  │ Downsample interval: [1 hour ▼]                     │   │
│  │                                                     │   │
│  │ Current data size: 256 MB                           │   │
│  │ Oldest record: Jan 1, 2025                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Account                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Username: admin                                     │   │
│  │                                                     │   │
│  │ Change Password                                     │   │
│  │ Current: [________]                                 │   │
│  │ New:     [________]                                 │   │
│  │ Confirm: [________]                                 │   │
│  │                                  [Update Password]  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  System Info                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ perf_events: ✓ Available                            │   │
│  │ Sampling interval: 5 seconds                        │   │
│  │ Version: 1.0.0                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                                      [Logout]               │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### MetricCard

```vue
<template>
  <div class="metric-card">
    <div class="card-header">
      <span class="icon">{{ icon }}</span>
      <span class="title">{{ title }}</span>
    </div>
    <div class="card-value">
      <span class="value">{{ value }}</span>
      <span class="unit">{{ unit }}</span>
    </div>
    <div class="card-chart">
      <slot name="chart"></slot>
    </div>
    <div class="card-details">
      <slot name="details"></slot>
    </div>
  </div>
</template>
```

**Props:**
- `title`: Card title (e.g., "CPU")
- `icon`: Icon name
- `value`: Main value (e.g., "76")
- `unit`: Unit (e.g., "%")

**Slots:**
- `chart`: ECharts component
- `details`: Additional metrics

---

### Chart Components

Each metric type has a dedicated chart component:

| Component | Chart Type | Data Points |
|-----------|------------|-------------|
| CpuChart | Stacked area (per-core) | 60 (5 min) |
| MemoryChart | Stacked area (breakdown) | 60 |
| NetworkChart | Line (in/out) | 60 |
| DiskChart | Line (read/write) | 60 |
| CacheChart | Bar (miss rates) | 60 |

### ECharts Configuration

```javascript
const baseChartOptions = {
  animation: false,  // Disable for real-time performance
  grid: {
    left: 40,
    right: 20,
    top: 20,
    bottom: 30
  },
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#f8fafc' }
  },
  xAxis: {
    type: 'time',
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#64748b' }
  },
  yAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#64748b' },
    splitLine: { lineStyle: { color: '#1e293b' } }
  }
};
```

---

## Responsive Design

### Breakpoints
```css
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
```

### Dashboard Grid
```css
/* Default: 2 columns */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

/* Mobile: 1 column */
@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## Loading States

### Initial Load
```
┌─────────────────────────┐
│ CPU                     │
│ ░░░░░░░░░░ --%         │
│ [Skeleton chart]        │
│                         │
│ Loading...              │
└─────────────────────────┘
```

### Connection Lost
```
┌─────────────────────────┐
│ CPU                     │
│ ████████░░ 76%         │
│ [Faded chart]           │
│                         │
│ ⚠️ Reconnecting...      │
└─────────────────────────┘
```

---

## Error States

### Metric Unavailable
```
┌─────────────────────────┐
│ Cache Performance       │
│                         │
│ ℹ️ perf_events not      │
│   available on this     │
│   system                │
│                         │
└─────────────────────────┘
```

### API Error
```
┌─────────────────────────┐
│ ⚠️ Failed to load data  │
│                         │
│ [Retry]                 │
└─────────────────────────┘
```

---

## Animations

### Transitions
```css
/* Value changes */
.metric-value {
  transition: color 0.3s ease;
}

/* Card interactions */
.metric-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
```

### Chart Updates
- No animation for real-time updates (performance)
- Smooth transition for data point additions
- Use `setOption({ notMerge: false })` for efficient updates
