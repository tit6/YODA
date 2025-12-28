<!-- Modal de création de partage -->
<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  create: [{
    documentName: string
    recipient: string
    duration: string
    accessType: 'read' | 'download'
    requirePassword: boolean
    password: string
    maxAccess: number | null
  }]
}>()

// Form pour créer un nouveau partage
const shareForm = ref({
  documentName: '',
  recipient: '',
  duration: '48',
  accessType: 'read' as 'read' | 'download',
  requirePassword: true,
  password: '',
  maxAccess: null as number | null
})

function handleClose() {
  emit('close')
}

const createShare = () => {
  emit('create', { ...shareForm.value })

  // Reset du formulaire
  shareForm.value = {
    documentName: '',
    recipient: '',
    duration: '48',
    accessType: 'read',
    requirePassword: true,
    password: '',
    maxAccess: null
  }
}

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
              <option value="Bilan 2024 - Confidentiel.pdf">Bilan 2024 - Confidentiel.pdf</option>
              <option value="Contrat Commercial 2024.pdf">Contrat Commercial 2024.pdf</option>
              <option value="Facture_2024_001.pdf">Facture_2024_001.pdf</option>
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

          <div class="input-row">
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
              <label for="access-type">Type d'accès</label>
              <select id="access-type" v-model="shareForm.accessType">
                <option value="read">Lecture seule</option>
                <option value="download">Téléchargement autorisé</option>
              </select>
            </div>
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

          <div class="checkbox-group">
            <input
              id="require-password"
              v-model="shareForm.requirePassword"
              type="checkbox"
            />
            <label for="require-password">Protéger par mot de passe</label>
          </div>

          <div v-if="shareForm.requirePassword" class="input-group">
            <label for="password">Mot de passe</label>
            <input
              id="password"
              v-model="shareForm.password"
              type="text"
              placeholder="Entrez un mot de passe"
              :required="shareForm.requirePassword"
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
  width: 60vh;
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