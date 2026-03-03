<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

type AdminUser = {
  id: number
  nom: string
  prenom: string
  email: string
  is_ban: number
  is_admin: number
}

const authStore = useAuthStore()

const users = ref<AdminUser[]>([])
const selectedUserId = ref<number | null>(null)
const isLoadingUsers = ref(false)
const isSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const selectedUser = computed(() =>
  users.value.find((user) => user.id === selectedUserId.value) ?? null
)

const toggleButtonLabel = computed(() => {
  if (!selectedUser.value) {
    return 'Changer le statut'
  }
  return selectedUser.value.is_ban === 1 ? 'Debannir l utilisateur' : 'Bannir l utilisateur'
})

const helperText = computed(() => {
  if (!selectedUser.value) {
    return 'Selectionne un utilisateur pour modifier son statut.'
  }

  return selectedUser.value.is_ban === 1
    ? 'Cet utilisateur est actuellement banni.'
    : 'Cet utilisateur est actuellement actif.'
})

async function fetchUsers() {
  isLoadingUsers.value = true
  errorMessage.value = ''

  try {
    const response = await fetch('/api/admin/users', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      credentials: 'include'
    })

    const data = await response.json()

    if (!response.ok || data.status === 'error') {
      throw new Error(data.message || data.error || 'Impossible de charger les utilisateurs.')
    }

    users.value = data.users ?? []
    if (users.value.length > 0) {
      const hasCurrentSelection = users.value.some((user) => user.id === selectedUserId.value)
      if (!hasCurrentSelection) {
        selectedUserId.value = users.value[0].id
      }
    } else {
      selectedUserId.value = null
    }
  } catch (error) {
    console.error('Erreur fetch users:', error)
    errorMessage.value = error instanceof Error ? error.message : 'Erreur de connexion au serveur.'
  } finally {
    isLoadingUsers.value = false
  }
}

async function toggleBanStatus() {
  successMessage.value = ''
  errorMessage.value = ''

  if (selectedUserId.value === null) {
    errorMessage.value = 'Selectionne un utilisateur.'
    return
  }

  isSubmitting.value = true

  try {
    const response = await fetch('/api/admin/toggle-ban', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        user_id: selectedUserId.value
      }),
      credentials: 'include'
    })

    const data = await response.json()

    if (!response.ok || data.status === 'error') {
      throw new Error(data.message || data.error || 'Impossible de modifier le statut utilisateur.')
    }

    successMessage.value = data.message || 'Statut utilisateur mis a jour.'
    await fetchUsers()
  } catch (error) {
    console.error('Erreur toggle ban user:', error)
    errorMessage.value = error instanceof Error ? error.message : 'Erreur de connexion au serveur.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <section class="admin-view">
    <form class="admin-card" @submit.prevent="toggleBanStatus">
      <p class="eyebrow">Administration</p>
      <h2 class="title">Gestion des utilisateurs</h2>
      <p class="description">
        Choisis un utilisateur dans la liste, puis inverse son statut de bannissement.
      </p>

      <label class="field-label" for="user-select">Utilisateur</label>
      <select
        id="user-select"
        v-model="selectedUserId"
        class="field-input"
        :disabled="isLoadingUsers || users.length === 0"
      >
        <option :value="null" disabled>
          {{ isLoadingUsers ? 'Chargement...' : 'Choisir un utilisateur' }}
        </option>
        <option v-for="user in users" :key="user.id" :value="user.id">
          {{ user.nom }} {{ user.prenom }} - {{ user.email }} - {{ user.is_ban === 1 ? 'Banni' : 'Actif' }}
        </option>
      </select>

      <div v-if="selectedUser" class="user-summary">
        <p><strong>ID :</strong> {{ selectedUser.id }}</p>
        <p><strong>Email :</strong> {{ selectedUser.email }}</p>
        <p><strong>Role :</strong> {{ selectedUser.is_admin === 1 ? 'Admin' : 'Utilisateur' }}</p>
        <p><strong>Statut :</strong> {{ selectedUser.is_ban === 1 ? 'Banni' : 'Actif' }}</p>
      </div>

      <p class="hint">{{ helperText }}</p>

      <button class="submit-button" type="submit" :disabled="isSubmitting || isLoadingUsers || !selectedUser">
        {{ isSubmitting ? 'Envoi...' : toggleButtonLabel }}
      </button>

      <p v-if="successMessage" class="feedback success">{{ successMessage }}</p>
      <p v-if="errorMessage" class="feedback error">{{ errorMessage }}</p>
    </form>
  </section>
</template>

<style scoped>
.admin-view {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  min-height: 100%;
}

.admin-card {
  width: min(720px, 100%);
  padding: 32px;
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #0f766e;
}

.title {
  margin: 0;
  font-size: 2rem;
  color: #0f172a;
}

.description {
  margin: 12px 0 24px;
  line-height: 1.6;
  color: #475569;
}

.field-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #0f172a;
}

.field-input {
  width: 100%;
  margin-bottom: 16px;
  padding: 14px 16px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  font-size: 1rem;
  color: #0f172a;
  background: #f8fafc;
}

.user-summary {
  margin: 8px 0 16px;
  padding: 16px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #0f172a;
}

.user-summary p {
  margin: 0 0 6px;
}

.user-summary p:last-child {
  margin-bottom: 0;
}

.hint {
  margin: 0 0 16px;
  color: #475569;
}

.submit-button {
  width: 100%;
  padding: 14px 16px;
  border: 0;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  color: #ffffff;
  background: #b91c1c;
  cursor: pointer;
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.feedback {
  margin: 16px 0 0;
  font-weight: 600;
}

.success {
  color: #15803d;
}

.error {
  color: #b91c1c;
}
</style>
