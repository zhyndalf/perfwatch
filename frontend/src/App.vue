<template>
  <div id="app">
    <header class="header">
      <h1>PerfWatch</h1>
      <p class="subtitle">Real-time System Performance Monitor</p>
    </header>

    <main class="main">
      <div class="status-card">
        <h2>Backend Status</h2>
        <div class="status" :class="backendStatus">
          {{ backendStatus === 'healthy' ? 'Connected' : 'Checking...' }}
        </div>
        <p v-if="backendInfo">{{ backendInfo.name }} v{{ backendInfo.version }}</p>
      </div>

      <div class="info-card">
        <h2>Getting Started</h2>
        <p>PerfWatch is a real-time system performance monitoring application.</p>
        <ul>
          <li>CPU, Memory, Disk, and Network metrics</li>
          <li>Real-time updates via WebSocket</li>
          <li>Interactive charts with ECharts</li>
          <li>Process monitoring</li>
        </ul>
      </div>
    </main>

    <footer class="footer">
      <p>PerfWatch v0.1.0 | Docker Setup Complete</p>
    </footer>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      backendStatus: 'checking',
      backendInfo: null,
    }
  },
  async mounted() {
    await this.checkBackend()
  },
  methods: {
    async checkBackend() {
      try {
        const response = await axios.get('/api/')
        this.backendInfo = response.data
        this.backendStatus = 'healthy'
      } catch (error) {
        // Try direct backend URL for development
        try {
          const response = await axios.get('http://localhost:8000/')
          this.backendInfo = response.data
          this.backendStatus = 'healthy'
        } catch {
          this.backendStatus = 'error'
        }
      }
    },
  },
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #eee;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header h1 {
  font-size: 2.5rem;
  background: linear-gradient(90deg, #00d4ff, #00ff88);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: #888;
  margin-top: 0.5rem;
}

.main {
  flex: 1;
  padding: 2rem;
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.status-card,
.info-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  min-width: 300px;
  max-width: 400px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.status-card h2,
.info-card h2 {
  margin-bottom: 1rem;
  color: #00d4ff;
}

.status {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.status.healthy {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.status.checking {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.status.error {
  background: rgba(255, 82, 82, 0.2);
  color: #ff5252;
}

.info-card ul {
  list-style: none;
  margin-top: 1rem;
}

.info-card li {
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
}

.info-card li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #00ff88;
}

.footer {
  text-align: center;
  padding: 1rem;
  color: #666;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
