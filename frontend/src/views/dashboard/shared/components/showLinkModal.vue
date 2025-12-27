<!-- Modal d'affichage du lien de partage -->
<script setup lang="ts">
const props = defineProps<{
  show: boolean
  link: string
  hasPassword: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

function handleClose() {
  emit('close')
}

const copyLink = () => {
  navigator.clipboard.writeText(props.link)
  alert('Lien copi� dans le presse-papiers !')
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="handleClose">
    <div class="modal modal-small">
      <div class="modal-header">
        <h2>Partage créé avec succès</h2>
      </div>

      <div class="modal-body">
        <div class="success-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="currentColor"/>
            <path d="M16.59 7.58L10 14.17L7.41 11.59L6 13L10 17L18 9L16.59 7.58Z" fill="currentColor"/>
          </svg>
        </div>

        <p class="success-message">Votre lien de partage a �t� cr��. Copiez-le et envoyez-le au destinataire.</p>

        <div class="link-box">
          <input type="text" :value="link" readonly class="link-input" />
          <button @click="copyLink" class="copy-btn">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 1H4C2.9 1 2 1.9 2 3V17H4V3H16V1ZM19 5H8C6.9 5 6 5.9 6 7V21C6 22.1 6.9 23 8 23H19C20.1 23 21 22.1 21 21V7C21 5.9 20.1 5 19 5ZM19 21H8V7H19V21Z" fill="currentColor"/>
            </svg>
            Copier
          </button>
        </div>

        <div class="info-box" v-if="hasPassword">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="currentColor"/>
          </svg>
          <p>N'oubliez pas de communiquer le mot de passe séparément au destinataire pour plus de sécurité.</p>
        </div>

        <div class="modal-actions">
          <button @click="handleClose" class="btn-primary full-width">
            Fermer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-small {
  max-width: 500px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 2px solid var(--border-input-color);
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.success-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px auto;
}

.success-icon svg {
  width: 80px;
  height: 80px;
  color: #00c851;
}

.success-message {
  text-align: center;
  font-size: 15px;
  color: var(--primary-hover-color);
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.link-box {
  display: flex;
  gap: 12px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 2px solid var(--border-input-color);
}

.link-input {
  flex: 1;
  padding: 8px 12px;
  border: none;
  background: white;
  border-radius: 6px;
  font-size: 13px;
  color: var(--primary-color);
  font-family: monospace;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.copy-btn:hover {
  background-color: var(--primary-hover-color);
}

.copy-btn svg {
  width: 16px;
  height: 16px;
}

.info-box {
  display: flex;
  gap: 12px;
  padding: 16px;
  background-color: #e3f2fd;
  border-radius: 8px;
  border-left: 4px solid #1976d2;
}

.info-box svg {
  width: 20px;
  height: 20px;
  color: #1976d2;
  flex-shrink: 0;
  margin-top: 2px;
}

.info-box p {
  font-size: 13px;
  color: #1565c0;
  margin: 0;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

.btn-primary {
  padding: 12px 24px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background-color: var(--primary-hover-color);
}

.full-width {
  width: 100%;
  justify-content: center;
}

/* Responsive */
@media (max-width: 768px) {
  .modal {
    max-width: 100%;
  }

  .modal-actions {
    flex-direction: column;
  }

  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
</style>
