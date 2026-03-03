<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

interface User {
  id: number
  nom: string
  prenom: string
  email: string
  is_admin: number
  is_active: number
}

const users = ref<User[]>([])
const loading = ref(true)
const error = ref('')
const togglingId = ref<number | null>(null)

async function fetchUsers() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('/api/admin/users', {
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        Accept: 'application/json',
      },
    })
    if (res.status === 403) {
      router.push('/dashboard/documents')
      return
    }
    const data = await res.json()
    if (data.status === 'success') {
      users.value = data.data
    } else {
      error.value = data.message || 'Erreur lors du chargement'
    }
  } catch (e) {
    error.value = 'Erreur réseau'
  } finally {
    loading.value = false
  }
}

async function toggleActive(user: User) {
  togglingId.value = user.id
  try {
    const res = await fetch(`/api/admin/users/${user.id}/toggle-active`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        Accept: 'application/json',
      },
    })
    const data = await res.json()
    if (data.status === 'success') {
      user.is_active = data.is_active
    }
  } catch (e) {
    console.error('Erreur toggle:', e)
  } finally {
    togglingId.value = null
  }
}

onMounted(() => {
  if (!authStore.isAdmin) {
    router.push('/dashboard/documents')
    return
  }
  fetchUsers()
})
</script>

<template>
  <div class="admin-panel">
    <div class="admin-header">
      <h2>Gestion des utilisateurs</h2>
      <p class="admin-subtitle">Activez ou désactivez les comptes utilisateurs</p>
    </div>

    <div v-if="loading" class="loading">Chargement...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>

    <div v-else class="users-table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nom</th>
            <th>Prénom</th>
            <th>Email</th>
            <th>Rôle</th>
            <th>Statut</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.nom }}</td>
            <td>{{ user.prenom }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span class="badge" :class="user.is_admin ? 'badge-admin' : 'badge-user'">
                {{ user.is_admin ? 'Admin' : 'Utilisateur' }}
              </span>
            </td>
            <td>
              <span class="badge" :class="user.is_active ? 'badge-active' : 'badge-inactive'">
                {{ user.is_active ? 'Actif' : 'Désactivé' }}
              </span>
            </td>
            <td>
              <button
                class="toggle-btn"
                :class="user.is_active ? 'btn-deactivate' : 'btn-activate'"
                :disabled="togglingId === user.id"
                @click="toggleActive(user)"
              >
                {{ togglingId === user.id ? '...' : user.is_active ? 'Désactiver' : 'Activer' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.admin-panel {
  max-width: 1000px;
  margin: 0 auto;
}

.admin-header {
  margin-bottom: var(--space-xxl, 32px);
}

.admin-header h2 {
  font-size: var(--font-size-3xl, 1.875rem);
  font-weight: var(--font-weight-bold, 700);
  color: var(--text-primary, #1a1a2e);
  margin-bottom: var(--space-sm, 8px);
}

.admin-subtitle {
  color: var(--text-muted, #6b7280);
  font-size: var(--font-size-md, 1rem);
}

.loading {
  text-align: center;
  padding: var(--space-xxl, 32px);
  color: var(--text-muted, #6b7280);
}

.error-msg {
  text-align: center;
  padding: var(--space-xl, 24px);
  color: var(--color-danger, #e74c3c);
  background: #fef2f2;
  border-radius: var(--border-radius-md, 8px);
}

.users-table-container {
  background: var(--bg-card, #ffffff);
  border-radius: var(--border-radius-lg, 12px);
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0,0,0,0.1));
  overflow: hidden;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  text-align: left;
  padding: 14px 16px;
  background-color: var(--bg-input-disabled, #f9fafb);
  font-size: var(--font-size-sm, 0.875rem);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--text-muted, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--border-color, #e5e7eb);
}

.users-table td {
  padding: 14px 16px;
  font-size: var(--font-size-base, 0.9375rem);
  color: var(--text-primary, #1a1a2e);
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.users-table tbody tr:hover {
  background-color: var(--bg-hover, #f3f4f6);
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: var(--font-size-xs, 0.75rem);
  font-weight: var(--font-weight-semibold, 600);
}

.badge-admin {
  background: #ede9fe;
  color: #7c3aed;
}

.badge-user {
  background: #e0f2fe;
  color: #0284c7;
}

.badge-active {
  background: #d1fae5;
  color: #059669;
}

.badge-inactive {
  background: #fee2e2;
  color: #dc2626;
}

.toggle-btn {
  padding: 6px 16px;
  border: none;
  border-radius: var(--border-radius-md, 8px);
  font-size: var(--font-size-sm, 0.875rem);
  font-weight: var(--font-weight-medium, 500);
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-deactivate {
  background: #fee2e2;
  color: #dc2626;
}

.btn-deactivate:hover:not(:disabled) {
  background: #fecaca;
}

.btn-activate {
  background: #d1fae5;
  color: #059669;
}

.btn-activate:hover:not(:disabled) {
  background: #a7f3d0;
}

@media (max-width: 768px) {
  .users-table-container {
    overflow-x: auto;
  }
}
</style>
