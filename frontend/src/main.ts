import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import '@/views/assets/variable.css'
import '@/views/assets/component.css'

// Intercepteur global : déconnexion automatique si le compte est désactivé (HTTP 460)
const originalFetch = window.fetch
window.fetch = async (...args) => {
  const response = await originalFetch(...args)
  if (response.status === 460) {
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()
    authStore.logout()
    router.push({ name: 'login', query: { disabled: '1' } })
  }
  return response
}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
