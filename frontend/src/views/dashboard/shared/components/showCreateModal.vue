<!-- Modal de création de partage -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useDocumentsStore } from '@/stores/documents'
import {useShareCryptoStore} from '@/stores/share_crypto'
import { useUsersStore } from '@/stores/users'


const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  create: [{
    documentName: string
    recipient: string
    duration: string
    password: string
    maxAccess: number | null
    token?: string
  }]
}>()

// Form pour créer un nouveau partage
const shareForm = ref({
  documentName: '',
  recipient: '',
  duration: '48',
  password: '',
  maxAccess: null as number | null
})

const userShareForm = ref({
  documentName: '',
  recipientUserId: null as number | null,
  duration: '48',
  password: '',
  maxAccess: null as number | null
})

function handleClose() {
  emit('close')
}

const createShareByEmail = async () => {
  try {
    const token = await shareCryptoStore.share_document(
      shareForm.value.documentName,
      shareForm.value.recipient,
      shareForm.value.duration,
      shareForm.value.maxAccess,
      shareForm.value.password
    )

    if (!token) {
      throw new Error('Token de partage manquant')
    }

    emit('create', {
      ...shareForm.value,
      token
    })

    // Reset du formulaire
    shareForm.value = {
      documentName: '',
      recipient: '',
      duration: '48',
      password: '',
      maxAccess: null
    }
  } catch (error) {
    console.error('Erreur lors de la création du partage', error)
  }
}

const createShareToUser = async () => {
  try {
    const recipientUserId = userShareForm.value.recipientUserId
    if (!recipientUserId) {
      throw new Error('Destinataire manquant')
    }

    const token = await shareCryptoStore.share_document_to_user(
      userShareForm.value.documentName,
      recipientUserId,
      userShareForm.value.duration,
      userShareForm.value.maxAccess,
      userShareForm.value.password
    )

    if (!token) {
      throw new Error('Token de partage manquant')
    }

    const user = usersStore.users.find(u => u.id === recipientUserId)
    const recipientLabel = user
      ? `${user.prenom} ${user.nom} (${user.email})`
      : `Utilisateur #${recipientUserId}`

    emit('create', {
      documentName: userShareForm.value.documentName,
      recipient: recipientLabel,
      duration: userShareForm.value.duration,
      password: userShareForm.value.password,
      maxAccess: userShareForm.value.maxAccess,
      token
    })

    userShareForm.value = {
      documentName: '',
      recipientUserId: null,
      duration: '48',
      password: '',
      maxAccess: null
    }
  } catch (error) {
    console.error('Erreur lors de la création du partage interne', error)
  }
}



//calling documents store to listen
const documentsStore = useDocumentsStore()
const usersStore = useUsersStore()

onMounted(async () => {
  await documentsStore.fetchAllDocuments()
  await usersStore.fetchUsers()
})

const shareCryptoStore = useShareCryptoStore()

</script>

<template>
  <div v-if="show" class="modal-overlay share-create-overlay" @click.self="handleClose">
      <div class="modal-content share-create-modal">
        <h3>Créer un nouveau partage</h3>

        <div class="forms-grid">
          <!-- Partage par email (existant) -->
          <form @submit.prevent="createShareByEmail" class="modal-body">
            <h4 class="form-title">Partager par email</h4>

            <div class="input-group">
              <label for="document-email">Document à partager</label>
              <select id="document-email" v-model="shareForm.documentName" required>
                <option value="">Sélectionner un document...</option>
                <option
                  v-for="doc in documentsStore.documents"
                  :key="doc.object_name"
                  :value="doc.object_name"
                >
                  {{ doc.folder_name ? `📁 ${doc.folder_name} / ${doc.file_name}` : doc.file_name }}
                </option>
                <option
                  v-if="!documentsStore.loading && documentsStore.documents.length === 0"
                  value=""
                  disabled
                >
                  Aucun document disponible
                </option>
              </select>
            </div>

            <div class="input-group">
              <label for="recipient-email">Email du destinataire</label>
              <input
                id="recipient-email"
                v-model="shareForm.recipient"
                type="email"
                placeholder="destinataire@exemple.com"
                required
              />
            </div>

            <div class="input-group">
              <label for="duration-email">Durée de validité</label>
              <select id="duration-email" v-model="shareForm.duration">
                <option value="1">1 heure</option>
                <option value="6">6 heures</option>
                <option value="24">24 heures</option>
                <option value="48">48 heures</option>
                <option value="168">7 jours</option>
                <option value="720">30 jours</option>
              </select>
            </div>

            <div class="input-group">
              <label for="max-access-email">Nombre d'accès maximum (optionnel)</label>
              <input
                id="max-access-email"
                v-model.number="shareForm.maxAccess"
                type="number"
                placeholder="Illimité"
                min="1"
              />
            </div>

            <div class="input-group">
              <label for="password-email">Mot de passe</label>
              <input
                id="password-email"
                v-model="shareForm.password"
                type="password"
                placeholder="Entrez un mot de passe"
              />
              <p class="input-hint">Ce mot de passe devra être communiqué au destinataire séparément.</p>
            </div>

            <div class="modal-actions">
              <button type="button" @click="handleClose" class="cancel-btn">
                Annuler
              </button>
              <button type="submit" class="confirm-btn">
                Créer le partage
              </button>
            </div>
          </form>

          <!-- Partage interne (nouveau) -->
          <form @submit.prevent="createShareToUser" class="modal-body">
            <h4 class="form-title">Partager à un utilisateur du site</h4>

            <div class="input-group">
              <label for="document-user">Document à partager</label>
              <select id="document-user" v-model="userShareForm.documentName" required>
                <option value="">Sélectionner un document...</option>
                <option
                  v-for="doc in documentsStore.documents"
                  :key="doc.object_name"
                  :value="doc.object_name"
                >
                  {{ doc.folder_name ? `📁 ${doc.folder_name} / ${doc.file_name}` : doc.file_name }}
                </option>
              </select>
            </div>

            <div class="input-group">
              <label for="recipient-user">Utilisateur</label>
              <select id="recipient-user" v-model="userShareForm.recipientUserId" required>
                <option :value="null">Sélectionner un utilisateur...</option>
                <option v-for="u in usersStore.users" :key="u.id" :value="u.id">
                  {{ u.prenom }} {{ u.nom }} ({{ u.email }})
                </option>
              </select>
            </div>

            <div class="input-group">
              <label for="duration-user">Durée de validité</label>
              <select id="duration-user" v-model="userShareForm.duration">
                <option value="1">1 heure</option>
                <option value="6">6 heures</option>
                <option value="24">24 heures</option>
                <option value="48">48 heures</option>
                <option value="168">7 jours</option>
                <option value="720">30 jours</option>
              </select>
            </div>

            <div class="input-group">
              <label for="max-access-user">Nombre d'accès maximum (optionnel)</label>
              <input
                id="max-access-user"
                v-model.number="userShareForm.maxAccess"
                type="number"
                placeholder="Illimité"
                min="1"
              />
            </div>

            <div class="input-group">
              <label for="password-user">Mot de passe</label>
              <input
                id="password-user"
                v-model="userShareForm.password"
                type="password"
                placeholder="Entrez un mot de passe"
              />
              <p class="input-hint">Optionnel: utile si vous souhaitez protéger le partage.</p>
            </div>

            <div class="modal-actions">
              <button type="button" @click="handleClose" class="cancel-btn">
                Annuler
              </button>
              <button type="submit" class="confirm-btn">
                Partager au membre
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
</template>

<style scoped>
.share-create-overlay {
  align-items: flex-start;
  padding: 24px;
}

.share-create-modal {
  max-width: 1100px;
  width: 100%;
  max-height: calc(100vh - 48px);
  overflow-y: auto;
  overflow-x: hidden;
}

.modal-body {
  min-width: 0;
  width: 100%;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: #f8f9fa;
  border: 1px solid var(--border-input-color);
  border-radius: 12px;
}

.forms-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}

.form-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--primary-color);
}

.input-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.input-hint {
  font-size: 12px;
  color: var(--primary-active-color);
  margin: 0;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.checkbox-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--primary-color);
  cursor: pointer;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

/* Responsive */
@media (max-width: 768px) {
  .forms-grid {
    grid-template-columns: 1fr;
  }

  .share-create-overlay {
    padding: 16px;
  }

  .share-create-modal {
    max-height: calc(100vh - 32px);
  }

  .input-row {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
