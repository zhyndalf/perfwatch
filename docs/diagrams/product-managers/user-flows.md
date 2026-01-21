# User Flows

> **End-to-end user journeys in PerfWatch**

This diagram shows the complete user experience from login to viewing real-time metrics and exploring historical data.

---

## Primary User Flow: Login to Dashboard

```mermaid
flowchart TD
    Start([User Opens Browser]) --> Login[Navigate to<br/>localhost:3000]
    Login --> CheckAuth{Authenticated?}

    CheckAuth -->|No| LoginPage[Display Login Page]
    LoginPage --> EnterCreds[Enter Username<br/>& Password]
    EnterCreds --> ClickLogin[Click 'Login' Button]
    ClickLogin --> ValidateCreds{Credentials<br/>Valid?}

    ValidateCreds -->|No| ShowError[Show Error:<br/>'Invalid credentials']
    ShowError --> EnterCreds

    ValidateCreds -->|Yes| SaveToken[Save JWT Token<br/>to localStorage]
    SaveToken --> RedirectDash[Redirect to<br/>Dashboard '/']

    CheckAuth -->|Yes| LoadDash[Load Dashboard Page]
    RedirectDash --> LoadDash

    LoadDash --> ConnectWS[Establish WebSocket<br/>Connection]
    ConnectWS --> WSSuccess{Connection<br/>Successful?}

    WSSuccess -->|No| ShowConnError[Show Error:<br/>'Unable to connect']
    ShowConnError --> RetryWS[Auto-retry Connection<br/>Exponential Backoff]
    RetryWS --> ConnectWS

    WSSuccess -->|Yes| StreamMetrics[Receive Metrics<br/>Every 5 Seconds]
    StreamMetrics --> UpdateCharts[Update 6 ECharts:<br/>CPU, Memory, Network,<br/>Disk, Perf, Bandwidth]
    UpdateCharts --> StreamMetrics

    UpdateCharts -.->|User Action| ViewHistory[Click 'History' Tab]
    ViewHistory --> HistoryPage[Load History Page]

    UpdateCharts -.->|User Action| ViewSettings[Click 'Settings' Tab]
    ViewSettings --> SettingsPage[Load Settings Page]

    UpdateCharts -.->|User Action| Logout[Click 'Logout']
    Logout --> ClearToken[Clear JWT Token]
    ClearToken --> DisconnectWS[Close WebSocket]
    DisconnectWS --> Login

    style Start fill:#4CAF50,color:#fff
    style LoginPage fill:#42A5F5,color:#fff
    style LoadDash fill:#66BB6A,color:#fff
    style StreamMetrics fill:#FFA726,color:#fff
    style ShowError fill:#EF5350,color:#fff
    style Logout fill:#78909C,color:#fff
```

---

## Historical Data Query Flow

```mermaid
flowchart TD
    History[User on History Page] --> SelectRange[Select Time Range<br/>Start & End Dates]
    SelectRange --> ClickQuery[Click 'Query' Button]
    ClickQuery --> ValidateRange{Time Range<br/>Valid?}

    ValidateRange -->|No| ShowValidationError[Show Error:<br/>'End must be after start']
    ShowValidationError --> SelectRange

    ValidateRange -->|Yes| SendRequest[Send GET Request<br/>/api/history/metrics]
    SendRequest --> ShowLoading[Show Loading Spinner]
    ShowLoading --> WaitResponse{Response<br/>Received?}

    WaitResponse -->|Timeout| ShowTimeout[Show Error:<br/>'Request timeout']
    ShowTimeout --> SelectRange

    WaitResponse -->|Success| CheckData{Data<br/>Available?}

    CheckData -->|No Data| ShowNoData[Show Message:<br/>'No data for this range']
    ShowNoData --> SelectRange

    CheckData -->|Has Data| RenderCharts[Render Historical<br/>Line Charts]
    RenderCharts --> DisplayMetrics[Display Time Series:<br/>CPU, Memory, Network, etc.]

    DisplayMetrics --> UserExplore[User Explores Data:<br/>Zoom, Pan, Hover]
    UserExplore -.->|New Query| SelectRange
    UserExplore -.->|Compare Mode| EnableCompare[Enable Comparison]

    EnableCompare --> ChooseMode{Choose<br/>Comparison Mode}

    ChooseMode -->|Relative| SelectPeriod[Select Period:<br/>hour, day, week]
    SelectPeriod --> SelectCompareTo[Select Compare To:<br/>yesterday, last_week]
    SelectCompareTo --> ClickCompare[Click 'Compare' Button]

    ChooseMode -->|Custom Range| SelectPeriod1[Select Period 1<br/>Start & End Dates]
    SelectPeriod1 --> SelectPeriod2[Select Period 2<br/>Start & End Dates]
    SelectPeriod2 --> ClickCompare

    ClickCompare --> SendCompareRequest[Send GET Request<br/>/api/history/compare]
    SendCompareRequest --> ShowCompareResults[Show Side-by-Side<br/>Comparison Charts & Stats]
    ShowCompareResults --> HighlightDiff[Highlight Differences:<br/>Green = Better<br/>Red = Worse]

    style History fill:#42A5F5,color:#fff
    style RenderCharts fill:#66BB6A,color:#fff
    style ShowNoData fill:#FFA726,color:#fff
    style ShowValidationError fill:#EF5350,color:#fff
    style ShowCompareResults fill:#AB47BC,color:#fff
```

---

## Settings Configuration Flow

```mermaid
flowchart TD
    Settings[User on Settings Page] --> ViewSystem[View System Info:<br/>Hostname, CPU, Memory]
    ViewSystem --> ViewRetention[View Current<br/>Retention Policy:<br/>30 days default]

    ViewRetention --> ModifyPolicy{Want to<br/>Modify?}

    ModifyPolicy -->|No| ViewOnly[View Only Mode]
    ViewOnly -.->|Navigate Away| Exit([Exit Settings])

    ModifyPolicy -->|Yes| ChangeDays[Change Retention Days<br/>Input Field]
    ChangeDays --> ClickSave[Click 'Save' Button]
    ClickSave --> ValidateDays{Days Valid?<br/>1-365}

    ValidateDays -->|No| ShowValidation[Show Error:<br/>'Must be 1-365 days']
    ShowValidation --> ChangeDays

    ValidateDays -->|Yes| SendUpdate[Send PUT Request<br/>/api/retention]
    SendUpdate --> ShowSaving[Show Saving Indicator]
    ShowSaving --> UpdateSuccess{Update<br/>Successful?}

    UpdateSuccess -->|No| ShowUpdateError[Show Error:<br/>'Failed to update']
    ShowUpdateError --> ChangeDays

    UpdateSuccess -->|Yes| ShowSuccess[Show Success:<br/>'Policy updated']
    ShowSuccess --> RefreshPolicy[Refresh Policy Display]

    RefreshPolicy --> TriggerCleanup{Trigger Manual<br/>Cleanup?}

    TriggerCleanup -->|No| Exit

    TriggerCleanup -->|Yes| ClickCleanup[Click 'Cleanup Now']
    ClickCleanup --> ConfirmCleanup{Confirm<br/>Action?}

    ConfirmCleanup -->|No| Exit

    ConfirmCleanup -->|Yes| SendCleanupRequest[Send POST Request<br/>/api/retention/cleanup]
    SendCleanupRequest --> ShowCleanupProgress[Show Progress:<br/>'Cleaning up...']
    ShowCleanupProgress --> CleanupComplete[Show Result:<br/>'Deleted X snapshots']
    CleanupComplete --> Exit

    style Settings fill:#42A5F5,color:#fff
    style ShowSuccess fill:#66BB6A,color:#fff
    style ShowValidation fill:#FFA726,color:#fff
    style ShowUpdateError fill:#EF5350,color:#fff
    style CleanupComplete fill:#AB47BC,color:#fff
```

---

## User Personas

### Primary User: System Administrator

**Profile:**
- Name: Alex (System Admin)
- Goal: Monitor Linux server performance in real-time
- Pain Points: Need quick visibility into system health, detect performance degradation
- Technical Level: High (comfortable with terminal, metrics)

**Use Cases:**
1. **Daily Health Check:**
   - Login → View dashboard → Check CPU/memory spikes → Logout
   - Time: 2 minutes

2. **Performance Investigation:**
   - Login → Notice high CPU → View history → Compare with yesterday → Identify issue
   - Time: 10 minutes

3. **Capacity Planning:**
   - Login → View history → Query last 30 days → Analyze trends → Export data (future)
   - Time: 30 minutes

4. **Cleanup Management:**
   - Login → Settings → Change retention to 7 days → Trigger cleanup → Verify space freed
   - Time: 5 minutes

---

## User Journey Touchpoints

### Login Experience

**First Time User:**
1. Open http://localhost:3000
2. See login form (clean, minimal)
3. Enter default credentials (admin/admin123)
4. Redirect to dashboard immediately

**Returning User:**
1. Open http://localhost:3000
2. Auto-login (JWT in localStorage)
3. Dashboard loads with live metrics

**Error State:**
- Invalid credentials → Red error message → Stay on login page
- Backend down → "Unable to connect" → Retry button

---

### Dashboard Experience

**On Load:**
- 6 charts appear (CPU, memory, network, disk, perf, bandwidth)
- "Connecting..." indicator while WebSocket establishes
- "Connected ✅" when live stream starts

**Live Updates:**
- Charts update every 5 seconds automatically
- No page refresh needed
- Current values displayed prominently

**Connection Loss:**
- "Disconnected ⚠️" warning appears
- Auto-reconnect attempts (exponential backoff)
- Charts freeze at last known values

**Navigation:**
- Sidebar: Dashboard, History, Settings
- Logout button in header
- Current time displayed

---

### History Experience

**Query Mode:**
- Date/time range picker (intuitive UI)
- "Query" button (disabled if range invalid)
- Loading spinner during fetch
- Charts render with historical data

**Comparison Mode:**
- Toggle "Compare" switch
- Two date range pickers (Period 1, Period 2)
- "Compare" button
- Side-by-side table with differences
- Color coding: Green (improvement), Red (regression)

**No Data State:**
- Friendly message: "No data available for this time range"
- Suggestion: "Try a different time range"

---

### Settings Experience

**System Info:**
- Read-only display (hostname, CPU count, total memory)
- Informational, no actions needed

**Retention Policy:**
- Current setting displayed prominently
- Input field for changing days
- Save button (validates 1-365)
- Success/error feedback

**Manual Cleanup:**
- "Cleanup Now" button
- Confirmation dialog: "Delete snapshots older than X days?"
- Progress indicator
- Result: "Deleted 15,000 snapshots, freed 150 MB"

---

## Edge Cases & Error Handling

### Authentication Errors

| Scenario | User Action | System Response |
|----------|-------------|-----------------|
| Wrong password | Enter credentials | "Invalid username or password" |
| JWT expired | Access protected page | Auto-logout, redirect to login |
| Backend down | Try to login | "Unable to connect to server. Please try again." |

---

### WebSocket Errors

| Scenario | User Action | System Response |
|----------|-------------|-----------------|
| Connection refused | Dashboard loads | "Connecting..." → "Failed to connect" → Retry |
| Connection lost | Viewing metrics | "Disconnected ⚠️" → Auto-reconnect → "Connected ✅" |
| Max retries reached | Wait 5 minutes | "Connection failed. Please refresh the page." |

---

### Query Errors

| Scenario | User Action | System Response |
|----------|-------------|-----------------|
| End before start | Click "Query" | "End time must be after start time" (validation) |
| No data in range | Query empty period | "No data available for this time range" |
| Query timeout | Large time range | "Request timeout. Try a shorter time range." |

---

### Settings Errors

| Scenario | User Action | System Response |
|----------|-------------|-----------------|
| Invalid retention days | Enter "0" or "1000" | "Retention must be between 1 and 365 days" |
| Update fails | Click "Save" | "Failed to update policy. Please try again." |
| Cleanup fails | Click "Cleanup Now" | "Cleanup failed. Please check logs." |

---

## Success Metrics

**User Engagement:**
- Average session duration: 5-10 minutes
- Login frequency: Daily (for active users)
- Feature usage: 80% dashboard, 15% history, 5% settings

**Performance:**
- Login to dashboard: < 2 seconds
- WebSocket connection: < 1 second
- Historical query: < 5 seconds (for 24h range)

**Reliability:**
- Uptime: 99.9%
- WebSocket reconnection success: > 95%
- Data freshness: 5-second interval consistently met

---

## Future Enhancements

**User-Requested Features:**
1. Export historical data (CSV, JSON)
2. Alerts on threshold violations
3. Custom dashboard layouts
4. Multi-server monitoring
5. Mobile app

**Priority:**
- P0: None (MVP complete)
- P1: Export data, alerts
- P2: Custom layouts
- P3: Multi-server, mobile

---

**Navigation:**
- [Next: WebSocket States →](./websocket-states.md)
- [↑ Back to Product Managers](./README.md)
- [↑ Diagrams Index](../README.md)
