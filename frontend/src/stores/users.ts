import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

export interface UserLite {
  id: number
  nom: string
  prenom: string
  email: string
}

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [] as UserLite[],
    loading: false,
    error: ''
  }),

  actions: {
    async fetchUsers(query: string = '') {
      this.loading = true
      this.error = ''
      try {
        const authStore = useAuthStore()
        const q = query.trim()
        const url = q
          ? `/api/users/list?q=${encodeURIComponent(q)}`
          : '/api/users/list'

        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const data = await response.json()
        if (data.status !== 'success') {
          throw new Error(data.message || 'Erreur inconnue')
        }

        this.users = (data.data?.users || []) as UserLite[]
      } catch (err) {
        this.error = String(err)
        console.error('Erreur fetchUsers:', err)
      } finally {
        this.loading = false
      }
    }
  }
})

