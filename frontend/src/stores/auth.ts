import { defineStore } from 'pinia'
import { jwtDecode } from "jwt-decode";
import { PrivateKey } from "@/stores/crypto.ts";


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
    const email = localStorage.getItem('auth_email') || ''

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
      email
    }
  },

  actions: {
    async register(data: { name: string; prenom: string; email: string; password: string; second_password: string }) {
      try {
        this.error = ''

        const res = await fetch('/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(data),
          credentials: 'include',
        })

        if (!res.ok) {
          const errorData = await res.json()
          this.error = errorData.error || 'Erreur lors de l\'enregistrement.'
          return false
        }

        const responseData = await res.json()

        if (responseData.status === 'error') {
          this.error = responseData.message || 'Erreur lors de l\'enregistrement.'
          return false
        }

        await PrivateKey.GeneratePrivateKey();

        return true

      } catch (err) {
        this.error = String(err)
        return false
      }
    },

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

        // Si l'API retourne un token c'est bon
        if (data.token) {
          this.token = data.token
          localStorage.setItem('auth_token', data.token)

          this.email = credentials.email
          localStorage.setItem('auth_email', this.email)

          // mettre à jour le 2FA à partir du JWT
          try {
            const decoded = jwtDecode<TokenJWT>(data.token)
            this.requires_a2f = decoded.a2f === 1
          } catch (err) {
            console.error("Erreur décodage JWT:", err)
            this.requires_a2f = false
          }

          this.isAuthenticated = true

          // Synchroniser la clé publique avec le backend après le login
          try {
            await PrivateKey.SyncPublicKeyToBackend()
          } catch (e) {
            console.error('Failed to sync public key:', e)
          }

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

    checkAuth() {
      const token = localStorage.getItem('auth_token')

      if (!token) {
        this.isAuthenticated = false
        this.requires_a2f = false
        return false
      }

      try {
        const decoded = jwtDecode<TokenJWT>(token)

        const currentTime = Math.floor(Date.now() / 1000)
        if (decoded.exp < currentTime) {
          this.logout()
          return false
        }

        return true

      } catch (err) {
        this.logout()
        return false
      }
    },

    logout() {
      this.isAuthenticated = false
      this.token = ''
      this.requires_a2f = false
      this.email = ''
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_email')
    },
  }
})
