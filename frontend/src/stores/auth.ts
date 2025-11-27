import { defineStore } from 'pinia'

type Credentials = { email: string; password: string }
type SessionJson = {
  authenticated?: boolean
  requires_a2f?: bigint
  error?: string
  status?: string
  token?: string
  message?: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    requires_a2f: BigInt(0),
    error: '',
  }),
  actions: {
      async login(credentials: Credentials) {
          try {
              this.error = ''
              const res = await fetch('/api/login', {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json',
                      'Accept': 'application/json',
                  },
                  body: JSON.stringify(credentials),
                  credentials: 'include',
              })

              if (!res.ok) {
                  const errorData = await res.json()
                  this.error = errorData.error || 'Mots de passe ou adresse email incorrects.'
                  this.isAuthenticated = false
                  return
              }

              const data = (await res.json()) as SessionJson

            if (data.error || data.status === 'error') {
                this.error = data.error || data.message || 'Erreur de connexion'
                this.isAuthenticated = false
                return
            }

            // Si l'API retourne un token, c'est que la connexion est réussie
            if (data.token || data.status === 'success') {
                this.isAuthenticated = true
            } else if (data.authenticated !== undefined) {
                this.error = 'Mots de passe ou adresse email incorrects.'
                this.isAuthenticated = data.authenticated
            }

            if (data.requires_a2f) {
                this.requires_a2f = data.requires_a2f
            }
          } catch (err) {
              this.error = 'Erreur de connexion'
              this.isAuthenticated = false
          }
      }
  }
})