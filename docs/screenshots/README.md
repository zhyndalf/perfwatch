# Screenshots

This directory contains application screenshots for documentation purposes.

## How to Add Screenshots

### 1. Capture Screenshots

**Dashboard:**
```bash
# Start the application
docker compose up -d

# Open browser and navigate to http://localhost:3000
# Login with admin/admin123
# Take screenshots of:
# - Login page
# - Dashboard with real-time metrics
# - History page with charts
# - Settings page
```

**Recommended Tools:**
- **macOS**: Cmd+Shift+4 (select area) or Cmd+Shift+3 (full screen)
- **Linux**: `gnome-screenshot` or `flameshot`
- **Windows**: Snipping Tool or Win+Shift+S

### 2. Optimize Screenshots

```bash
# Resize to reasonable width (max 1200px)
convert dashboard.png -resize 1200x dashboard-optimized.png

# Or use online tools:
# - TinyPNG: https://tinypng.com/
# - Squoosh: https://squoosh.app/
```

### 3. Save to This Directory

**Naming Convention:**
- `01-login.png` - Login page
- `02-dashboard.png` - Main dashboard with metrics
- `03-dashboard-charts.png` - Close-up of charts
- `04-history.png` - Historical metrics view
- `05-history-comparison.png` - Time period comparison
- `06-settings.png` - Settings page
- `07-websocket-connection.png` - Real-time connection indicator

### 4. Update README.md

Add screenshot references to the main README.md in the "Screenshots" section.

## Current Screenshots

<!-- Add screenshots here as you create them -->

| Screenshot | Description | Status |
|------------|-------------|--------|
| 01-login.png | Login page with credentials form | ⏳ TODO |
| 02-dashboard.png | Real-time metrics dashboard | ⏳ TODO |
| 03-dashboard-charts.png | ECharts visualizations | ⏳ TODO |
| 04-history.png | Historical data query interface | ⏳ TODO |
| 05-history-comparison.png | Time period comparison table | ⏳ TODO |
| 06-settings.png | System info and retention policy | ⏳ TODO |
| 07-websocket-connection.png | Live connection status | ⏳ TODO |

## Screenshot Guidelines

**Best Practices:**
- ✅ Use default theme (dark mode if applicable)
- ✅ Show realistic data (not empty states)
- ✅ Capture at 1920x1080 or higher resolution
- ✅ Include browser chrome if showing URL
- ✅ Optimize file size (< 500KB per image)
- ✅ Use PNG format for UI screenshots
- ❌ Don't include sensitive system information
- ❌ Don't show actual production hostnames/IPs

**Dimensions:**
- Full page: 1920x1080
- Focused view: 1200x800
- Detail shot: 800x600

## Placeholder Images

Until actual screenshots are available, the README uses:
- Mermaid diagrams for architecture visualization
- Text descriptions for feature highlights
- Links to live demo (if available)
