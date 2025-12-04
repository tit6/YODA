import { defineStore } from 'pinia'
import { jwtDecode } from "jwt-decode";

type Credentials = { email: string; password: string }
type SessionJson = {
  authenticated?: boolean
  requires_a2f?: boolean
  error?: string
  status?: string
  token?: string
  message?: string
}

interface TokenJWT {
    id: number
    a2f: number
    exp: number
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    const token = localStorage.getItem('auth_token') || ''

    let requiresA2F = false

    if (token) {
      try {
        const decoded = jwtDecode<TokenJWT>(token)
        requiresA2F = decoded.a2f === 1
      } catch (err) {
        console.warn("JWT invalide ou expiré", err)
      }
    }

    return {
      isAuthenticated: !!token,
      requires_a2f: requiresA2F,
      error: '',
      token,
    }
  },

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

        // Si l'API retourne un token → login OK
        if (data.token) {
          this.token = data.token
          localStorage.setItem('auth_token', data.token)

          // 🔥 IMPORTANT : mettre à jour le 2FA à partir du JWT
          try {
            const decoded = jwtDecode<TokenJWT>(data.token)
            this.requires_a2f = decoded.a2f === 1
          } catch (err) {
            console.error("Erreur décodage JWT:", err)
            this.requires_a2f = false
          }

          this.isAuthenticated = true
          return
        }

        // Si pas de token mais authenticated est fourni
        if (data.authenticated !== undefined) {
          this.error = 'Mots de passe ou adresse email incorrects.'
          this.isAuthenticated = data.authenticated
        }

      } catch (err) {
        this.error = 'Erreur de connexion'
        this.isAuthenticated = false
      }
    },

    logout() {
      this.isAuthenticated = false
      this.token = ''
      this.requires_a2f = false
      localStorage.removeItem('auth_token')
    },
  }
})
