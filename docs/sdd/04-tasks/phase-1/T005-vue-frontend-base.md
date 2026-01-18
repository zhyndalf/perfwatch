# T005: Vue Frontend Base

## Metadata

| Field | Value |
|-------|-------|
| **Phase** | 1 - Foundation |
| **Estimated Time** | 2-3 hours |
| **Dependencies** | T002 (Docker Setup) |
| **Status** | ⬜ NOT_STARTED |

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
- [ ] Vite + Vue 3 initialized
- [ ] Vue Router configured
- [ ] Pinia store setup
- [ ] TailwindCSS integrated
- [ ] Axios configured with base URL

### Pages/Views
- [ ] `Login.vue` - Login form
- [ ] `Dashboard.vue` - Placeholder (empty)
- [ ] `History.vue` - Placeholder (empty)
- [ ] `Settings.vue` - Placeholder (empty)

### Components
- [ ] `Header.vue` - Navigation header
- [ ] `Layout.vue` - Main layout wrapper

### Auth Flow
- [ ] Auth store (Pinia) with login/logout
- [ ] Token storage in localStorage
- [ ] Route guards for protected pages
- [ ] Redirect to login when unauthenticated
- [ ] Axios interceptor for auth header

### Styling
- [ ] Dark theme CSS variables
- [ ] Login page matches design
- [ ] Responsive on mobile

---

## Implementation Details

### Project Structure

```
frontend/src/
├── main.js              # Entry point
├── App.vue              # Root component
├── router/
│   └── index.js         # Route definitions
├── stores/
│   └── auth.js          # Auth state
├── views/
│   ├── Login.vue
│   ├── Dashboard.vue
│   ├── History.vue
│   └── Settings.vue
├── components/
│   └── layout/
│       ├── Header.vue
│       └── Layout.vue
├── composables/
│   └── useAuth.js       # Auth helper
├── api/
│   └── index.js         # Axios instance
└── styles/
    └── main.css         # Global styles
```

### Router Setup

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && auth.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
```

### Auth Store (Pinia)

```javascript
import { defineStore } from 'pinia'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token'),
    user: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    async login(username, password) {
      const response = await api.post('/auth/login', { username, password })
      this.token = response.data.access_token
      localStorage.setItem('token', this.token)
      await this.fetchUser()
    },

    async fetchUser() {
      const response = await api.get('/auth/me')
      this.user = response.data
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
```

### API Setup (Axios)

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

### Login Component Skeleton

```vue
<template>
  <div class="login-container">
    <div class="login-card">
      <h1>PerfWatch</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Username</label>
          <input v-model="username" type="text" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" required />
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
```

---

## Files to Create

| File | Description |
|------|-------------|
| `frontend/package.json` | Dependencies |
| `frontend/vite.config.js` | Vite config |
| `frontend/tailwind.config.js` | Tailwind config |
| `frontend/postcss.config.js` | PostCSS config |
| `frontend/index.html` | HTML template |
| `frontend/src/main.js` | Entry point |
| `frontend/src/App.vue` | Root component |
| `frontend/src/router/index.js` | Routes |
| `frontend/src/stores/auth.js` | Auth store |
| `frontend/src/views/*.vue` | Page components |
| `frontend/src/components/layout/*.vue` | Layout components |
| `frontend/src/api/index.js` | Axios setup |
| `frontend/src/styles/main.css` | Global styles |

---

## Verification Steps

```bash
# Install dependencies
cd frontend && npm install

# Start dev server
npm run dev

# Access login page
open http://localhost:5173/login

# Test login flow
# 1. Enter admin/admin123
# 2. Should redirect to dashboard
# 3. Refresh page - should stay logged in
# 4. Check Network tab for API calls
# 5. Test logout
```

---

## Implementation Notes

*To be filled during implementation*

---

## Files Created/Modified

*To be filled during implementation*
