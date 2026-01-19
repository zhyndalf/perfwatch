# T012: Dashboard UI

> **Status**: IN_PROGRESS  
> **Phase**: 2 - Core Metrics  
> **Estimated Time**: 3-4 hours

---

## Objective

Implement the real-time dashboard UI that consumes the WebSocket metrics stream and renders CPU, Memory, Network, and Disk charts per the UI specification.

---

## Requirements

1. **WebSocket Integration**
   - Use the `/api/ws/metrics` endpoint with JWT from the auth store
   - Auto-reconnect on close; show connection status (Connected/Disconnected/Retrying)
   - Handle `ping/pong` keepalive if needed
2. **Dashboard Layout (Desktop & Mobile)**
   - Fixed grid layout per UI spec: CPU, Memory, Network, Disk cards
   - Dark theme colors from UI spec variables; consistent typography
   - Responsive: 2-column desktop, stacked on mobile
3. **Charts (ECharts)**
   - CPU: per-core line/stacked bar + headline usage percent
   - Memory: usage percent + used/total; include swap if available
   - Network: bandwidth up/down over time; show current rates
   - Disk: read/write throughput over time; show current rates
4. **Data Handling**
   - Update charts every 5s from WebSocket stream; maintain rolling window (e.g., last 5-10 minutes, capped points)
   - Graceful degradation: display “N/A” when metric field missing; avoid crashes
   - Show last update timestamp and sample interval (5s)
5. **UX/State**
   - Loading state until first message; error state on auth failure/WS error
   - Visible status chip: Connected / Reconnecting / Disconnected
   - Basic accessibility: semantic headings, aria labels on buttons/toggles

---

## Acceptance Criteria

- Frontend connects to `/api/ws/metrics` with stored JWT and automatically reconnects after disconnects.
- Dashboard shows four cards (CPU, Memory, Network, Disk) with charts updating every 5 seconds using live data.
- Connection status and last update time are visible and accurate.
- UI does not crash if any metric field is missing; shows “N/A” or hides unavailable details.
- Works on desktop (2-column) and mobile (stacked) layouts.

---

## Implementation Status

### Completed ✅
- WebSocket integration in frontend (JWT, auto-reconnect, status chip, last update)
- Dashboard layout built with ECharts charts for CPU/Memory/Network/Disk (rolling window, N/A safe)
- Responsive grid (2-col desktop, stacked mobile), dark theme styles

### Pending ⏳
- Additional polish/QA on mobile interactions
- Manual UX pass once more data sources land (advanced metrics, history)

---

## Verification

1. Login to frontend, navigate to dashboard.
2. Observe connection status becomes “Connected”; last update timestamp updates every ~5s.
3. Confirm charts update live for CPU, Memory, Network, Disk and degrade gracefully if a field is missing (e.g., disconnect collector).
4. Simulate disconnect (stop backend or drop network) and verify auto-reconnect and status transitions.
