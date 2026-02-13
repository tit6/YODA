<!-- Modal de création de partage -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useDocumentsStore } from '@/stores/documents'
import {useShareCryptoStore} from '@/stores/share_crypto'


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

function handleClose() {
  emit('close')
}

const createShare = async () => {
  try {
    const token = await shareCryptoStore.share_document(
      shareForm.value.documentName,
      shareForm.value.recipient,
      shareForm.value.duration,
      shareForm.value.maxAccess,
      shareForm.value.password
    )

    console.log('Token du partage créé :', token)

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



//calling documents store to listen
const documentsStore = useDocumentsStore()

onMounted(async () => {
  await documentsStore.fetchAllDocuments()
})

const shareCryptoStore = useShareCryptoStore()

</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="handleClose">
      <div class="modal-content">
        <h3>Créer un nouveau partage</h3>

        <form @submit.prevent="createShare" class="modal-body">
          <div class="input-group">
            <label for="document">Document à partager</label>
            <select id="document" v-model="shareForm.documentName" required>
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
            <label for="recipient">Email du destinataire</label>
            <input
              id="recipient"
              v-model="shareForm.recipient"
              type="email"
              placeholder="destinataire@exemple.com"
              required
            />
          </div>


          <div class="input-group">
            <label for="duration">Durée de validité</label>
            <select id="duration" v-model="shareForm.duration">
              <option value="1">1 heure</option>
              <option value="6">6 heures</option>
              <option value="24">24 heures</option>
              <option value="48">48 heures</option>
              <option value="168">7 jours</option>
              <option value="720">30 jours</option>
            </select>
          </div>


          <div class="input-group">
            <label for="max-access">Nombre d'accès maximum (optionnel)</label>
            <input
              id="max-access"
              v-model.number="shareForm.maxAccess"
              type="number"
              placeholder="Illimité"
              min="1"
            />
          </div>

          <div class="input-group">
            <label for="password">Mot de passe</label>
            <input
              id="password"
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
      </div>
    </div>
</template>

<style scoped>
.modal-body {
  width: 55vh;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
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
  .input-row {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
