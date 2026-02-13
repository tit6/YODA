import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

export interface Document {
  object_name: string
  file_name: string
  size: number
  last_modified: string
  dek_encrypted: string
  iv: string
  sha256: string
  folder_name?: string | null
}

export interface Folder {
  id: number
  name: string
  created_at: string
}

export interface BreadcrumbItem {
  id: number
  name: string
}

export const useDocumentsStore = defineStore('documents', {
  state: () => ({
    documents: [] as Document[],
    folders: [] as Folder[],
    breadcrumb: [] as BreadcrumbItem[],
    currentFolderId: null as number | null,
    loading: false,
    error: ''
  }),

  actions: {
    async fetchDocuments(folderId: number | null = null) {
      this.loading = true
      this.error = ''
      this.currentFolderId = folderId

      try {
        const authStore = useAuthStore()
        const url = folderId !== null
          ? `/api/documents/list?folder_id=${folderId}`
          : '/api/documents/list'
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error('Erreur lors de la récupération des documents')
        }

        const data = await response.json()
        if (data.status === 'success') {
          this.documents = data.data.documents
          this.folders = data.data.folders || []
          this.breadcrumb = data.data.breadcrumb || []
        } else {
          this.error = data.message || 'Erreur inconnue'
        }
      } catch (err) {
        this.error = String(err)
        console.error('Erreur fetchDocuments:', err)
      } finally {
        this.loading = false
      }
    },

    async fetchAllDocuments() {
      this.loading = true
      this.error = ''

      try {
        const authStore = useAuthStore()
        const response = await fetch('/api/documents/list?all=true', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error('Erreur lors de la récupération des documents')
        }

        const data = await response.json()
        if (data.status === 'success') {
          this.documents = data.data.documents
          this.folders = []
          this.breadcrumb = []
        } else {
          this.error = data.message || 'Erreur inconnue'
        }
      } catch (err) {
        this.error = String(err)
        console.error('Erreur fetchAllDocuments:', err)
      } finally {
        this.loading = false
      }
    },

    async createFolder(name: string, parentId: number | null = null) {
      this.loading = true
      this.error = ''

      try {
        const authStore = useAuthStore()
        const response = await fetch('/api/documents/folders/create', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ name, parent_id: parentId })
        })

        if (!response.ok) {
          throw new Error('Erreur lors de la création du dossier')
        }

        const data = await response.json()
        if (data.status === 'success') {
          await this.fetchDocuments(this.currentFolderId)
          return true
        } else {
          this.error = data.message || 'Erreur inconnue'
          return false
        }
      } catch (err) {
        this.error = String(err)
        console.error('Erreur createFolder:', err)
        return false
      } finally {
        this.loading = false
      }
    },

    async deleteFolder(folderId: number) {
      this.loading = true
      this.error = ''

      try {
        const authStore = useAuthStore()
        const response = await fetch(`/api/documents/folders/delete/${folderId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })

        if (!response.ok) {
          throw new Error('Erreur lors de la suppression du dossier')
        }

        const data = await response.json()
        if (data.status === 'success') {
          await this.fetchDocuments(this.currentFolderId)
          return true
        } else {
          this.error = data.message || 'Erreur inconnue'
          return false
        }
      } catch (err) {
        this.error = String(err)
        console.error('Erreur deleteFolder:', err)
        return false
      } finally {
        this.loading = false
      }
    },

    async uploadDocument(payload: {
      file_name: string
      file_data: string
      dek_encrypted: string
      iv: string
      sha256: string
      folder_id?: number | null
    }) {
      this.loading = true
      this.error = ''

      try {
        const authStore = useAuthStore()
        const response = await fetch('/api/documents/upload', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })

        if (!response.ok) {
          throw new Error('Erreur lors de l\'upload du document')
        }

        const data = await response.json()
        if (data.status === 'success') {
          // Rafraîchir la liste
          await this.fetchDocuments(this.currentFolderId)
          return true
        } else {
          this.error = data.message || 'Erreur inconnue'
          return false
        }
      } catch (err) {
        this.error = String(err)
        console.error('Erreur uploadDocument:', err)
        return false
      } finally {
        this.loading = false
      }
    },

    async uploadDocument_shared(payload: {
      file_name: string
      file_data: string
      dek_encrypted: string
      iv: string
      sha256: string
      email?: string
      time?: string
      number_of_accesses?: number | null
      source_object_name?: string
    }): Promise<{
      status: 'success'
      token: string
    } | null> {
      this.loading = true
      this.error = ''

      try {
        const authStore = useAuthStore()
        const response = await fetch('/api/share/upload', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })

        let data: any = null
        const contentType = response.headers.get('content-type') || ''
        if (contentType.includes('application/json')) {
          data = await response.json()
        } else {
          const text = await response.text()
          data = text ? { message: text } : null
        }

        if (!response.ok) {
          const message = data?.message || data?.error || `HTTP ${response.status}`
          this.error = message
          console.error('Erreur uploadDocument_shared:', response.status, data)
          return null
        }

        if (data?.status === 'success') {
          // Rafraîchir la liste
          await this.fetchDocuments(this.currentFolderId)
          return data
        } else {
          this.error = data?.message || 'Erreur inconnue'
          return null
        }
      } catch (err) {
        this.error = String(err)
        console.error('Erreur uploadDocument:', err)
        return null
      } finally {
        this.loading = false
      }
    },

    async downloadDocument(objectName: string): Promise<{
      blob: Blob,
      fileName: string,
      dekEncrypted: string,
      iv: string,
      sha256: string
    } | null> {
      try {
        const authStore = useAuthStore()
        const response = await fetch(`/api/documents/download/${encodeURIComponent(objectName)}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })

        if (!response.ok) {
          throw new Error('Erreur lors du téléchargement')
        }

        // Récupérer les métadonnées des headers
        const dekEncrypted = response.headers.get('X-DEK-Encrypted') || ''
        const iv = response.headers.get('X-IV') || ''
        const sha256 = response.headers.get('X-SHA256') || ''

        // Extraire le nom du fichier du header Content-Disposition
        const contentDisposition = response.headers.get('Content-Disposition') || ''
        let fileName = 'document'
        const matches = /filename="?([^"]+)"?/.exec(contentDisposition)
        if (matches && matches[1]) {
          fileName = matches[1]
        }

        const blob = await response.blob()

        return {
          blob,
          fileName,
          dekEncrypted,
          iv,
          sha256
        }
      } catch (err) {
        this.error = String(err)
        console.error('Erreur downloadDocument:', err)
        return null
      }
    },

    async deleteDocument(objectName: string) {
      this.loading = true
      this.error = ''

      try {
        const authStore = useAuthStore()
        const response = await fetch(`/api/documents/delete/${encodeURIComponent(objectName)}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })

        if (!response.ok) {
          throw new Error('Erreur lors de la suppression')
        }

        const data = await response.json()
        if (data.status === 'success') {
          // Rafraîchir la liste
          await this.fetchDocuments(this.currentFolderId)
          return true
        } else {
          this.error = data.message || 'Erreur inconnue'
          return false
        }
      } catch (err) {
        this.error = String(err)
        console.error('Erreur deleteDocument:', err)
        return false
      } finally {
        this.loading = false
      }
    },

    navigateToFolder(folderId: number | null) {
      this.fetchDocuments(folderId)
    }
  }
})
