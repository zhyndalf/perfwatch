# T005: Vue Frontend Base

## Metadata

| Field | Value |
|-------|-------|
| **Phase** | 1 - Foundation |
| **Estimated Time** | 2-3 hours |
| **Dependencies** | T002 (Docker Setup), T004 (Auth Backend) |
| **Status** | ✅ COMPLETED |
| **Completed** | 2026-01-19 |

---

## Objective

Set up Vue.js 3 application with Vite, Vue Router, Pinia, TailwindCSS, and implement the login page.

---

## Context

The frontend needs:
- Vue 3 with Composition API
- Vite for fast development
- Vue Router for navigation
- Pinia for state management
- TailwindCSS for styling
- Axios for API calls

This task focuses on auth flow; dashboard comes in Phase 2.

---

## Specifications

Reference documents:
- [UI Spec - Login Page](../../02-specification/ui-spec.md#login-page-login)
- [Architecture - Frontend](../../02-specification/architecture.md#frontend-components)

---

## Acceptance Criteria

### Project Setup
- [x] Vite + Vue 3 initialized
- [x] Vue Router configured
- [x] Pinia store setup
- [x] TailwindCSS integrated
- [x] Axios configured with base URL

### Pages/Views
- [x] `Login.vue` - Login form
- [x] `Dashboard.vue` - Placeholder
- [x] `History.vue` - Placeholder
- [x] `Settings.vue` - Placeholder with password change

### Components
- [x] `Header.vue` - Navigation header with logout
- [x] `Layout.vue` - Main layout wrapper

### Auth Flow
- [x] Auth store (Pinia) with login/logout
- [x] Token storage in localStorage
- [x] Route guards for protected pages
- [x] Redirect to login when unauthenticated
- [x] Axios interceptor for auth header

### Styling
- [x] Dark theme CSS variables
- [x] Login page matches design
- [x] TailwindCSS with custom colors

---

## Implementation Notes

### Key Decisions

1. **JSON body for login** - Backend expects JSON `LoginRequest` schema, not form-urlencoded
2. **Vite alias** - Added `@` alias in vite.config.js for cleaner imports
3. **Conditional layout** - App.vue shows Layout only for authenticated routes
4. **Lazy-loaded routes** - All views use dynamic imports for code splitting

### Issues Resolved

- Fixed login API: Changed from form-urlencoded to JSON body to match backend `LoginRequest` schema

---

## Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `frontend/package.json` | Modified | Added pinia, tailwindcss, postcss, autoprefixer |
| `frontend/tailwind.config.js` | Created | Dark theme colors configuration |
| `frontend/postcss.config.js` | Created | PostCSS with Tailwind/Autoprefixer |
| `frontend/vite.config.js` | Modified | Added @ alias for src directory |
| `frontend/src/api/index.js` | Created | Axios client with JWT interceptors |
| `frontend/src/stores/auth.js` | Created | Pinia auth store (login, logout, fetchUser) |
| `frontend/src/router/index.js` | Created | Vue Router with navigation guards |
| `frontend/src/views/Login.vue` | Created | Full login form with validation |
| `frontend/src/views/Dashboard.vue` | Created | Placeholder with metric card placeholders |
| `frontend/src/views/History.vue` | Created | Placeholder for historical data |
| `frontend/src/views/Settings.vue` | Created | Password change form, user info |
| `frontend/src/components/layout/Layout.vue` | Created | Main layout wrapper |
| `frontend/src/components/layout/Header.vue` | Created | Navigation header with logout |
| `frontend/src/styles/main.css` | Created | Tailwind directives and custom styles |
| `frontend/src/main.js` | Modified | Added Pinia, Router, styles import |
| `frontend/src/App.vue` | Modified | RouterView with conditional layout |

---

## Verification Results

```bash
# Login API test
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# ✅ Returns: {"access_token":"...","token_type":"bearer","expires_in":86400}

# Auth me test
curl http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer <token>"
# ✅ Returns: {"id":1,"username":"admin",...}

# Frontend serving
curl http://localhost:3000/login
# ✅ Returns HTML with Vue app
```

---

## Testing Checklist

- [x] Open http://localhost:3000 - redirects to /login
- [x] Login with admin/admin123 - redirects to dashboard
- [x] Refresh page - stays logged in (token persisted)
- [x] Click logout - redirects to login
- [x] Access /settings when logged out - redirects to login
