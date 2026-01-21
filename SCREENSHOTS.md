# Adding Screenshots to PerfWatch

This guide helps contributors capture and add screenshots to the README.

## Quick Steps

1. **Start PerfWatch**
2. **Capture screenshots** of each page
3. **Optimize images** (resize, compress)
4. **Save to docs/screenshots/**
5. **Update README.md** (replace placeholder links)

---

## Detailed Instructions

### Step 1: Start the Application

```bash
# Clone and setup
git clone https://github.com/zhyndalf/perfwatch.git
cd perfwatch
make setup

# Or manual setup
docker compose up -d
docker compose exec backend alembic upgrade head

# Wait for services to be ready
make health
```

**Access:**
- Frontend: http://localhost:3000
- Login: `admin` / `admin123`

---

### Step 2: Capture Screenshots

#### Required Screenshots

| Filename | Page | What to Capture | Tips |
|----------|------|-----------------|------|
| `01-login.png` | Login | Login form with username/password fields | Show empty fields or partially filled |
| `02-dashboard.png` | Dashboard | Full dashboard with all 6 charts showing data | Wait 10-15 seconds for metrics to populate |
| `03-dashboard-charts.png` | Dashboard | Close-up of 2-3 charts | Show chart details (tooltips, legends) |
| `04-history.png` | History | Historical query interface with date pickers and charts | Show a populated chart from a query |
| `05-history-comparison.png` | History | Comparison table showing two time periods | Enable comparison mode first |
| `06-settings.png` | Settings | System info and retention policy settings | Show filled retention days input |
| `07-websocket-connection.png` | Dashboard | Connection status indicator (top-right) | Zoom in on the status badge |

#### Capturing Tips

**For macOS:**
```bash
# Capture selection (Cmd+Shift+4)
# - Click and drag to select area
# - Files saved to ~/Desktop/

# Capture window (Cmd+Shift+4, then Space)
# - Click on browser window
# - Includes window shadow
```

**For Linux:**
```bash
# Using gnome-screenshot
gnome-screenshot -a  # Select area
gnome-screenshot -w  # Current window

# Using flameshot (recommended)
flameshot gui
```

**For Windows:**
```bash
# Windows Snipping Tool
Win+Shift+S  # Select area
# Or use Snipping Tool app
```

---

### Step 3: Optimize Screenshots

#### Resize (if needed)

```bash
# Using ImageMagick
convert dashboard.png -resize 1200x dashboard.png

# Using sips (macOS)
sips -Z 1200 dashboard.png

# Online tools:
# - https://squoosh.app/
# - https://tinypng.com/
```

**Target Dimensions:**
- Full page: 1200px width (maintain aspect ratio)
- Close-up: 800px width
- Detail: 600px width

#### Compress

**Target file sizes:**
- < 300KB for full page
- < 200KB for close-ups
- < 100KB for details

**Tools:**
```bash
# Using pngquant
pngquant --quality=65-80 dashboard.png

# Using OptiPNG
optipng -o7 dashboard.png

# Online:
# - https://tinypng.com/ (drag and drop)
```

---

### Step 4: Save Screenshots

```bash
# Move to screenshots directory
mv *.png docs/screenshots/

# Verify
ls -lh docs/screenshots/
# Should show all 7 PNG files
```

**File naming:**
```
docs/screenshots/
├── 01-login.png
├── 02-dashboard.png
├── 03-dashboard-charts.png
├── 04-history.png
├── 05-history-comparison.png
├── 06-settings.png
└── 07-websocket-connection.png
```

---

### Step 5: Update README.md

The README already has placeholder sections. **No changes needed!**

The screenshot sections use relative paths:
```markdown
![Login Page](./docs/screenshots/01-login.png)
```

Once you save the screenshots with the correct filenames, they'll automatically display in the README.

---

## Screenshot Guidelines

### ✅ Do's

- **Use realistic data**: Let the app run for 10-15 seconds to collect real metrics
- **Show live state**: Connection indicator showing "Connected", active charts
- **Capture at high resolution**: 1920x1080 or higher, then resize
- **Include context**: Show browser chrome if demonstrating URL
- **Use dark theme** (if app supports it, or document which theme)
- **Consistent timing**: Capture all screenshots in one session for consistency

### ❌ Don'ts

- **Don't show sensitive info**: Actual server hostnames, IPs, or passwords
- **Don't use empty states**: Wait for data to populate
- **Don't capture at low resolution**: Start high, resize down
- **Don't skip compression**: Keep GitHub repo size reasonable
- **Don't include personal data**: Desktop icons, bookmarks, other apps

---

## Advanced: Creating Animated GIFs

For dynamic features (WebSocket reconnection, chart updates):

### Using Peek (Linux)

```bash
# Install Peek
sudo apt install peek

# Record
peek
# Select area → Record → Stop → Save as GIF
```

### Using LICEcap (macOS/Windows)

1. Download from https://www.cockos.com/licecap/
2. Select area and record
3. Save as GIF

**Example GIF ideas:**
- `websocket-reconnect.gif` - Show auto-reconnection flow
- `realtime-updates.gif` - Show metrics updating in real-time
- `history-query.gif` - Show query process from start to result

---

## Quality Checklist

Before committing screenshots:

- [ ] All 7 required screenshots captured
- [ ] Images optimized (< 300KB each)
- [ ] Correct filenames (01-login.png, 02-dashboard.png, etc.)
- [ ] Saved to `docs/screenshots/` directory
- [ ] No sensitive information visible
- [ ] Images show realistic, populated data
- [ ] README displays images correctly (test locally)

---

## Testing Locally

```bash
# View README with screenshots in browser
# (Requires grip or similar Markdown previewer)

# Install grip
pip install grip

# Preview README
grip README.md

# Or push to a branch and view on GitHub
git checkout -b add-screenshots
git add docs/screenshots/*.png
git commit -m "Add application screenshots"
git push origin add-screenshots
# View on GitHub in the branch
```

---

## Example Workflow

```bash
# 1. Start app
make setup

# 2. Capture screenshots (using Flameshot on Linux)
flameshot gui
# Save as: ~/Desktop/screenshot1.png, screenshot2.png, etc.

# 3. Rename and move
cd ~/Desktop
mv screenshot1.png 01-login.png
mv screenshot2.png 02-dashboard.png
# ... (rename all)

# 4. Optimize
for file in *.png; do
  pngquant --quality=65-80 "$file" --output "docs/screenshots/$file"
done

# 5. Verify
ls -lh docs/screenshots/
# All files < 300KB

# 6. Commit
git add docs/screenshots/*.png
git commit -m "Add application screenshots"
git push
```

---

## Alternative: Video Demo

Instead of screenshots, consider recording a video demo:

**Platforms:**
- **YouTube**: Upload unlisted video, embed in README
- **Asciinema**: Terminal recording (for CLI interactions)
- **Loom**: Quick screen recording with narration

**Example README addition:**
```markdown
## Video Demo

[![PerfWatch Demo](./docs/screenshots/video-thumbnail.png)](https://youtube.com/watch?v=...)

*Click to watch a 2-minute demo of PerfWatch in action*
```

---

## Getting Help

**Questions?**
- Open an issue: https://github.com/zhyndalf/perfwatch/issues
- Tag: `documentation`, `help wanted`

**Resources:**
- [GitHub Markdown Guide](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [Image Optimization Best Practices](https://web.dev/fast/#optimize-your-images)

---

**Thank you for contributing screenshots! 📸**
