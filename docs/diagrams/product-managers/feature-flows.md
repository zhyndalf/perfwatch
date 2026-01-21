# Feature Flows

> **Key feature pipelines and system workflows**

This document shows the end-to-end flow of major features in PerfWatch.

---

## Metrics Collection Pipeline

```mermaid
flowchart TD
    Start([Every 5 Seconds]) --> BGTask[Background Task<br/>Triggered]
    BGTask --> Aggregator[MetricsAggregator<br/>collect_all]

    Aggregator --> Parallel{Collect in Parallel}

    Parallel --> CPU[CPUCollector<br/>psutil.cpu_percent]
    Parallel --> Memory[MemoryCollector<br/>psutil.virtual_memory]
    Parallel --> Network[NetworkCollector<br/>psutil.net_io_counters]
    Parallel --> Disk[DiskCollector<br/>psutil.disk_io_counters]
    Parallel --> Perf[PerfEventsCollector<br/>perf_event_open]
    Parallel --> Bandwidth[MemoryBandwidthCollector<br/>/proc/vmstat]

    CPU --> CheckCPU{Success?}
    Memory --> CheckMem{Success?}
    Network --> CheckNet{Success?}
    Disk --> CheckDisk{Success?}
    Perf --> CheckPerf{Success?}
    Bandwidth --> CheckBand{Success?}

    CheckCPU -->|Yes| CPUData[CPU Metrics]
    CheckCPU -->|No| CPUNull[None Graceful Degradation]

    CheckMem -->|Yes| MemData[Memory Metrics]
    CheckMem -->|No| MemNull[None]

    CheckNet -->|Yes| NetData[Network Metrics]
    CheckNet -->|No| NetNull[None]

    CheckDisk -->|Yes| DiskData[Disk Metrics]
    CheckDisk -->|No| DiskNull[None]

    CheckPerf -->|Yes| PerfData[Perf Metrics]
    CheckPerf -->|No| PerfNull[None No perf_events]

    CheckBand -->|Yes| BandData[Bandwidth Metrics]
    CheckBand -->|No| BandNull[None]

    CPUData --> Combine[Combine Results]
    CPUNull --> Combine
    MemData --> Combine
    MemNull --> Combine
    NetData --> Combine
    NetNull --> Combine
    DiskData --> Combine
    DiskNull --> Combine
    PerfData --> Combine
    PerfNull --> Combine
    BandData --> Combine
    BandNull --> Combine

    Combine --> Snapshot[Create Snapshot<br/>JSON with timestamp]

    Snapshot --> Split{Distribute}

    Split --> Database[BatchMetricsWriter<br/>Queue for DB]
    Split --> WebSocket[WebSocket Manager<br/>Broadcast to clients]

    Database --> BatchCheck{Batch Size<br/>>= 10?}
    BatchCheck -->|No| QueueWait[Keep in queue]
    BatchCheck -->|Yes| BulkInsert[Bulk INSERT<br/>PostgreSQL]
    BulkInsert --> DBDone[Stored in<br/>metrics_snapshot]

    WebSocket --> SendToClients[Send JSON to<br/>Connected Clients]
    SendToClients --> ClientUpdate[Client receives<br/>Updates UI]

    ClientUpdate --> End([Wait 5s])
    DBDone --> End
    QueueWait --> End
    End --> Start

    style Start fill:#4CAF50,color:#fff
    style Combine fill:#FFA726,color:#fff
    style Snapshot fill:#42A5F5,color:#fff
    style BulkInsert fill:#66BB6A,color:#fff
    style SendToClients fill:#AB47BC,color:#fff
    style End fill:#78909C,color:#fff
```

---

## Data Retention Lifecycle

```mermaid
flowchart TD
    Start([Application Startup]) --> InitPolicy[Load Archive Policy<br/>Default: 30 days]
    InitPolicy --> StartLoop[Start Background Task<br/>retention_cleanup_loop]

    StartLoop --> Wait[Wait 1 Hour<br/>RETENTION_CLEANUP_INTERVAL]
    Wait --> WakeUp[Task Wakes Up]

    WakeUp --> FetchPolicy[Fetch Archive Policy<br/>FROM archive_policy]
    FetchPolicy --> CalcCutoff[Calculate Cutoff Date<br/>NOW - retention_days]

    CalcCutoff --> Example[Example:<br/>2026-01-21 - 30 days<br/>= 2025-12-22]

    Example --> DeleteQuery[DELETE FROM metrics_snapshot<br/>WHERE timestamp < cutoff]
    DeleteQuery --> Execute[Execute Deletion]

    Execute --> CountDeleted[Count Deleted Rows]
    CountDeleted --> LogResult[Log Result:<br/>'Deleted X snapshots']

    LogResult --> Vacuum{Should<br/>VACUUM?}
    Vacuum -->|No| NextCycle[Sleep 1 Hour]
    Vacuum -->|Yes| VacuumDB[VACUUM ANALYZE<br/>Reclaim Disk Space]
    VacuumDB --> NextCycle

    NextCycle --> Wait

    Wait -.->|Manual Trigger| ManualCleanup[User clicks<br/>'Cleanup Now']
    ManualCleanup --> APICall[POST /api/retention/cleanup]
    APICall --> FetchPolicy

    style Start fill:#4CAF50,color:#fff
    style CalcCutoff fill:#FFA726,color:#fff
    style Execute fill:#EF5350,color:#fff
    style LogResult fill:#42A5F5,color:#fff
    style VacuumDB fill:#66BB6A,color:#fff
```

---

## Historical Comparison Workflow

```mermaid
flowchart TD
    Start([User on History Page]) --> EnableCompare[Enable Comparison Mode<br/>Toggle Switch]

    EnableCompare --> ChooseMode{Choose<br/>Comparison Mode}

    ChooseMode -->|Relative| SelectPeriod[Select Period:<br/>hour, day, week]
    SelectPeriod --> SelectCompareTo[Select Compare To:<br/>yesterday, last_week]
    SelectCompareTo --> ValidateRelative{Inputs<br/>Valid?}

    ChooseMode -->|Custom Range| SelectP1[Select Period 1<br/>Date Range]
    SelectP1 --> SelectP2[Select Period 2<br/>Date Range]
    SelectP2 --> ValidateCustom{Periods<br/>Same Duration?}

    ValidateRelative -->|No| ShowRelativeError[Show Validation Error]
    ValidateCustom -->|No| ShowCustomError[Show Error:<br/>'Periods must be same duration']
    ShowRelativeError --> SelectPeriod
    ShowCustomError --> SelectP2

    ValidateRelative -->|Yes| ClickCompare[Click 'Compare' Button]
    ValidateCustom -->|Yes| ClickCompare

    ClickCompare --> SendRequest[GET /api/history/compare<br/>with mode-specific params]

    SendRequest --> BackendReceive[Backend Receives Request]
    BackendReceive --> QueryP1[Query Period 1<br/>SELECT * FROM metrics_snapshots<br/>WHERE timestamp BETWEEN...]
    BackendReceive --> QueryP2[Query Period 2<br/>SELECT * FROM metrics_snapshots<br/>WHERE timestamp BETWEEN...]

    QueryP1 --> Agg1[Process Period 1:<br/>Extract data_points]
    QueryP2 --> Agg2[Process Period 2:<br/>Extract data_points]

    Agg1 --> CalcSummary[Calculate Summary Stats:<br/>current_avg, comparison_avg]
    Agg2 --> CalcSummary

    CalcSummary --> CalcPercent[Calculate Change %:<br/>(comparison - current) / current * 100]

    CalcPercent --> BuildResponse[Build Response JSON:<br/>current, comparison, summary]

    BuildResponse --> SendResponse[Send 200 OK<br/>with Comparison Data]

    SendResponse --> FrontendReceive[Frontend Receives Response]
    FrontendReceive --> RenderCharts[Render Comparison Charts:<br/>Overlay Time Series]

    RenderCharts --> ShowSummary[Display Summary Stats]
    ShowSummary --> HighlightPos[Highlight Improvements<br/>Green]
    ShowSummary --> HighlightNeg[Highlight Degradations<br/>Red]

    HighlightPos --> Display[Display to User]
    HighlightNeg --> Display

    Display --> UserAnalyze[User Analyzes Differences<br/>Identifies Trends]

    UserAnalyze --> NewCompare{New<br/>Comparison?}
    NewCompare -->|Yes| ChooseMode
    NewCompare -->|No| End([Exit Comparison Mode])

    style Start fill:#42A5F5,color:#fff
    style CalcSummary fill:#FFA726,color:#fff
    style HighlightPos fill:#66BB6A,color:#fff
    style HighlightNeg fill:#EF5350,color:#fff
    style Display fill:#AB47BC,color:#fff
```

---

## Authentication & Authorization Flow

```mermaid
flowchart TD
    Start([User Opens App]) --> CheckToken{JWT Token<br/>in localStorage?}

    CheckToken -->|No| ShowLogin[Show Login Page]
    ShowLogin --> EnterCreds[User Enters<br/>Username & Password]
    EnterCreds --> SubmitLogin[Click 'Login']

    SubmitLogin --> APILogin[POST /api/auth/login]
    APILogin --> ValidateCreds[Backend Validates<br/>Credentials]

    ValidateCreds --> CheckHash{bcrypt<br/>Password Match?}

    CheckHash -->|No| Return401[Return 401 Unauthorized]
    Return401 --> ShowError[Show Error:<br/>'Invalid credentials']
    ShowError --> EnterCreds

    CheckHash -->|Yes| CreateJWT[Create JWT Token<br/>Expires in 24h]
    CreateJWT --> UpdateLogin[Update last_login<br/>in Database]
    UpdateLogin --> ReturnToken[Return Access Token<br/>+ Token Type]

    ReturnToken --> SaveToken[Frontend Saves Token<br/>to localStorage]
    SaveToken --> Redirect[Redirect to Dashboard]

    CheckToken -->|Yes| ValidateToken[Validate Token<br/>GET /api/auth/me]
    ValidateToken --> DecodeJWT{JWT Valid<br/>& Not Expired?}

    DecodeJWT -->|No| ClearToken[Clear localStorage]
    ClearToken --> ShowLogin

    DecodeJWT -->|Yes| FetchUser[Fetch User Data<br/>from Database]
    FetchUser --> LoadDash[Load Dashboard]

    Redirect --> LoadDash

    LoadDash --> ConnectWS[Connect WebSocket<br/>with JWT in URL]
    ConnectWS --> Authenticated[User Authenticated ✅<br/>Access Granted]

    Authenticated --> UserAction{User Action}
    UserAction -->|API Call| AddHeader[Axios Interceptor<br/>Adds 'Authorization: Bearer JWT']
    UserAction -->|WebSocket| UseTokenParam[Token in Query Param<br/>?token=JWT]
    UserAction -->|Logout| Logout[Click Logout]

    Logout --> ClearState[Clear Auth State<br/>Remove localStorage Token]
    ClearState --> DisconnectWS[Close WebSocket]
    DisconnectWS --> ShowLogin

    style Start fill:#4CAF50,color:#fff
    style CheckHash fill:#FFA726,color:#fff
    style CreateJWT fill:#42A5F5,color:#fff
    style SaveToken fill:#66BB6A,color:#fff
    style Authenticated fill:#AB47BC,color:#fff
    style ShowError fill:#EF5350,color:#fff
```

---

## Real-Time Dashboard Update Flow

```mermaid
flowchart TD
    Start([Dashboard Page Loaded]) --> Mount[Vue Component<br/>onMounted Hook]
    Mount --> CheckAuth{User<br/>Authenticated?}

    CheckAuth -->|No| Redirect[Redirect to Login]
    CheckAuth -->|Yes| ConnectWS[metricsStore.connect]

    ConnectWS --> OpenWS[Open WebSocket<br/>ws://localhost:8000/api/ws/metrics]
    OpenWS --> WSHandshake[WebSocket Handshake<br/>101 Switching Protocols]

    WSHandshake --> WSReady[WebSocket Ready<br/>connectionState = 'connected']

    WSReady --> WaitMessage[Wait for Message<br/>from Backend]

    WaitMessage --> ReceiveJSON[onmessage Event<br/>Receive JSON Payload]
    ReceiveJSON --> ParseJSON[Parse JSON<br/>Extract Metrics]

    ParseJSON --> UpdateStore[Update metricsStore.currentMetrics<br/>Vue Reactive State]

    UpdateStore --> Reactivity[Vue Reactivity<br/>Triggers Re-render]

    Reactivity --> UpdateCPU[Update CPU Chart<br/>ECharts.setOption]
    Reactivity --> UpdateMem[Update Memory Chart]
    Reactivity --> UpdateNet[Update Network Chart]
    Reactivity --> UpdateDisk[Update Disk Chart]
    Reactivity --> UpdatePerf[Update Perf Chart]
    Reactivity --> UpdateBand[Update Bandwidth Chart]

    UpdateCPU --> ChartRender[Charts Re-render<br/>Smooth Animation]
    UpdateMem --> ChartRender
    UpdateNet --> ChartRender
    UpdateDisk --> ChartRender
    UpdatePerf --> ChartRender
    UpdateBand --> ChartRender

    ChartRender --> UpdateTimestamp[Update 'Last Updated'<br/>Timestamp Display]

    UpdateTimestamp --> WaitNext[Wait for Next Message<br/>5 Seconds]

    WaitNext --> WaitMessage

    WaitMessage -.->|Connection Lost| HandleClose[onclose Event]
    HandleClose --> ShowDisconnected[Show 'Disconnected'<br/>Warning]
    ShowDisconnected --> AttemptReconnect[Auto-reconnect Logic<br/>Exponential Backoff]
    AttemptReconnect --> ConnectWS

    WaitMessage -.->|User Navigates Away| Unmount[Vue Component<br/>onBeforeUnmount]
    Unmount --> CloseWS[metricsStore.disconnect<br/>Close WebSocket]
    CloseWS --> End([End Session])

    style Start fill:#4CAF50,color:#fff
    style UpdateStore fill:#FFA726,color:#fff
    style Reactivity fill:#42A5F5,color:#fff
    style ChartRender fill:#AB47BC,color:#fff
    style ShowDisconnected fill:#EF5350,color:#fff
```

---

## Feature Summary

### Metrics Collection

**Frequency:** Every 5 seconds
**Collectors:** 6 parallel collectors (CPU, memory, network, disk, perf_events, memory_bandwidth)
**Output:** Single JSON snapshot
**Distribution:** WebSocket broadcast (real-time) + Database persistence (historical)
**Graceful Degradation:** Missing collectors return None, frontend shows "N/A"

---

### Data Retention

**Trigger:** Every 1 hour (configurable)
**Policy:** Delete snapshots older than N days (default: 30)
**Execution:** Single DELETE query with timestamp filter
**Cleanup:** Optional VACUUM to reclaim disk space
**Manual:** User can trigger immediate cleanup via Settings

---

### Historical Comparison

**Input:** Two time periods (start/end dates)
**Query:** Two aggregate queries (AVG metrics per period)
**Calculation:** Difference and percentage change
**Output:** Side-by-side comparison table
**UI:** Color-coded improvements (green) and regressions (red)

---

### Authentication

**Method:** JWT (JSON Web Token)
**Storage:** localStorage (frontend persistent)
**Expiry:** 24 hours
**Refresh:** Manual re-login (no automatic refresh)
**Security:** bcrypt password hashing (cost factor 12)

---

### Real-Time Dashboard

**Transport:** WebSocket (persistent connection)
**Frequency:** Metrics pushed every 5 seconds
**Reactivity:** Vue.js reactive state updates
**Visualization:** ECharts library (6 charts)
**Reconnection:** Automatic with exponential backoff

---

## Performance Characteristics

### Metrics Collection
- **Latency:** 10-50ms per collector
- **Total Time:** ~100ms (parallel collection)
- **CPU Overhead:** ~2% (100ms every 5s)
- **Memory:** ~50 KB state storage

### Database Operations
- **Insertion:** Batch write (10 snapshots → 50s)
- **Query (1 hour):** ~10ms (with index)
- **Query (24 hours):** ~50ms (with index)
- **Deletion (1 day):** ~1-2 seconds

### WebSocket Performance
- **Connection Time:** < 1 second
- **Message Size:** ~2 KB per snapshot
- **Bandwidth:** 0.4 KB/s per client
- **Concurrent Clients:** 100+ supported

---

**Navigation:**
- [← Previous: WebSocket States](./websocket-states.md)
- [↑ Back to Product Managers](./README.md)
- [↑ Diagrams Index](../README.md)
