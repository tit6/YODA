import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

export interface SharedDocument {
  id: string
  documentName: string
  recipient: string
  createdAt: string
  expiresAt: string
  accessType: 'read' | 'download'
  hasPassword: boolean
  link: string
  token?: string
  accessCount: number
  maxAccess?: number
  view_count?: number
  status: string
}

export interface SharedDocumentApi {
  id: number
  object_name: string
  file_name: string
  destination_email: string
  expires_at: string
  token?: string
  size: number
  last_modified: string
  max_views?: number
  views_count?: number
  is_active: number
  dek_encrypted?: string
  iv?: string
  sha256?: string
}

export interface CreateSharePayload {
  documentName: string
  recipient: string
  duration: string
  password?: string
  maxAccess: number | null
  token?: string
  accessType?: 'read' | 'download'
  requirePassword?: boolean
}

export const useShareFonctionStore = defineStore('share_fonction', {
  state: () => ({
    sharedDocuments: [] as SharedDocument[],
    loading: false,
    error: '',
    generatedLink: '',
    generatedLinkHasPassword: false,
    showCreateModalVisible: false,
    showLinkModalVisible: false
  }),

  actions: {
    buildShareLink(token?: string) {
      if (!token) return ''
      const origin = typeof window !== 'undefined' ? window.location.origin : 'https://localhost:5173'
      return `${origin}/s/${token}`
    },

    formatDate(value: string) {
      const parsed = new Date(value)
      return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString('fr-FR')
    },

    createShare(formData: CreateSharePayload) {
      if (!formData.token) {
        this.error = 'Token manquant'
        return
      }

      const hasPassword = typeof formData.requirePassword === 'boolean'
        ? formData.requirePassword
        : Boolean(formData.password)

      this.generatedLink = this.buildShareLink(formData.token)
      this.generatedLinkHasPassword = hasPassword

      let hoursToAdd = Number.parseInt(formData.duration, 10)
      if (Number.isNaN(hoursToAdd)) {
        hoursToAdd = 0
      }

      const expiresAt = new Date()
      expiresAt.setHours(expiresAt.getHours() + hoursToAdd)

      this.sharedDocuments.unshift({
        id: String(Date.now()),
        documentName: formData.documentName,
        recipient: formData.recipient,
        createdAt: new Date().toLocaleString('fr-FR'),
        expiresAt: expiresAt.toLocaleString('fr-FR'),
        accessType: formData.accessType || 'download',
        hasPassword: hasPassword,
        link: this.generatedLink,
        token: formData.token,
        accessCount: 0,
        maxAccess: formData.maxAccess || undefined,
        view_count: 0,
        status: '0'
      })

      this.showCreateModalVisible = false
      this.showLinkModalVisible = true
    },

    async fetchSharedDocuments() {
      this.loading = true
      this.error = ''

      try {
        const authStore = useAuthStore()
        const response = await fetch('/api/share/list', {
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

        const documents = (data.data?.documents || []) as SharedDocumentApi[]
        this.sharedDocuments = documents.map((doc) => ({
          id: String(doc.id),
          documentName: doc.file_name,
          recipient: doc.destination_email || '-',
          createdAt: this.formatDate(doc.last_modified),
          expiresAt: this.formatDate(doc.expires_at),
          accessType: 'download',
          hasPassword: false,
          link: this.buildShareLink(doc.token),
          token: doc.token,
          accessCount: 0,
          maxAccess: doc.max_views,
          view_count: doc.views_count ?? 0,
          status: doc.is_active ? '0' : '1'
        }))
      } catch (err) {
        this.error = String(err)
        console.error('Erreur fetchSharedDocuments:', err)
      } finally {
        this.loading = false
      }
    },

    filterDocuments(query: string) {
      const normalized = query.trim().toLowerCase()
      if (!normalized) return this.sharedDocuments

      return this.sharedDocuments.filter(doc =>
        doc.documentName.toLowerCase().includes(normalized) ||
        doc.recipient.toLowerCase().includes(normalized)
      )
    },

    async revokeShare(shareId: string) {
      const share = this.sharedDocuments.find(s => s.id === shareId)
      if (!share) {
        return
      }
      const actionLabel = share.status === '0' ? 'revoquer' : 'reactiver'
      if (confirm(`Etes-vous sur de vouloir ${actionLabel} le partage de "${share.documentName}" ?`)) {
        try {
          const authStore = useAuthStore()
          const response = await fetch('/api/share/switch', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: shareId })
          })

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
          }

          const data = await response.json()
          if (data.status !== 'success') {
            throw new Error(data.message || 'Erreur inconnue')
          }

          share.status = share.status === '0' ? '1' : '0'
        } catch (err) {
          this.error = String(err)
          console.error('Erreur revokeShare:', err)
        }
      }
    },

    async deleteShare(shareId: string) {
      const share = this.sharedDocuments.find(s => s.id === shareId)
      if (share && confirm('Etes-vous sur de vouloir supprimer definitivement ce partage ?')) {
        const index = this.sharedDocuments.findIndex(s => s.id === shareId)
        try {
          const authStore = useAuthStore()
          const response = await fetch('/api/share/delete', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: shareId })
          })

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
          }

          const data = await response.json()
          if (data.status !== 'success') {
            throw new Error(data.message || 'Erreur inconnue')
          }
          if (index !== -1) {
            this.sharedDocuments.splice(index, 1)
          }
        } catch (err) {
          this.error = String(err)
          console.error('Erreur deleteShare:', err)
        }
      }
    },

    getStatusColor(status: string) {
      switch (status) {
        case '0': return '#00c851'
        case '1': return '#ffaa00'
        default: return '#999'
      }
    },

    getStatusText(status: string) {
      switch (status) {
        case '0': return 'Actif'
        case '1': return 'Revoque'
        default: return status
      }
    },

    openShareLink(share: SharedDocument) {
      this.generatedLink = share.link || this.buildShareLink(share.token)
      this.generatedLinkHasPassword = share.hasPassword
      this.showLinkModalVisible = true
    }
  }
})
