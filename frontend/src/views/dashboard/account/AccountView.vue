<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const showPasswordModal = ref(false)
const showA2FModal = ref(false)
const showDisableA2FModal = ref(false)
const password = ref('')
const otpcode = ref('')
const qrCodeBase64 = ref('')
const secretKey = ref('')
const disablePassword = ref('')
const disableOtp = ref('')
const isA2FActive = ref(false)

async function check_password_a2f() {
  if (isA2FActive.value) {
    showDisableA2FModal.value = true
  } else {
    showPasswordModal.value = true
  }
}

function closePasswordModal() {
  showPasswordModal.value = false
  password.value = ''
}

async function confirmPassword() {
  try {
    const response = await fetch('/api/active_a2f', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ password: password.value }),
      credentials: 'include'
    })

    const data = await response.json()

    if (response.ok && data.status === 'success') {
      showPasswordModal.value = false
      showA2FModal.value = true

      qrCodeBase64.value = data.qrcode
      secretKey.value = data.secret || ''

    } else {
      console.log(data.error)
      alert('Mot de passe incorrect')
    }
  } catch (error) {
    console.error('Erreur:', error)
    alert('Erreur de connexion')
  }
}

function closeA2FModal() {
  showA2FModal.value = false
}

async function status_a2f() {
  const response = await fetch('/api/statue_a2f', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      credentials: 'include'
    })

  let data = await response.json()
  let statusss = document.getElementById("status_a2f")
  let btn = document.getElementById("a2f_button");

  if (data.status === 2) {
    isA2FActive.value = true
    if (statusss && btn) {
      statusss.classList.add("active")
      statusss.textContent = "Activée"
      btn.textContent = "Désactiver";
      btn.style.backgroundColor = "#EF1C43";
    }
  } else {
    isA2FActive.value = false
    if (statusss && btn) {
      statusss.classList.add("inactive")
      statusss.textContent = "Désactivée"
      btn.textContent = "Activer";
    }
  }

}

async function confirmA2F() {
  const response = await fetch('/api/check_a2f', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ otp: otpcode.value }),
      credentials: 'include'
    })

  let data = await response.json()

  if (data.status === 'success') {
    await status_a2f();
    showA2FModal.value = false
  } else {
    alert("non.")
  }
}

function copySecretKey() {
  navigator.clipboard.writeText(secretKey.value)
    .then(() => alert('Clé secrète copiée!'))
    .catch(() => alert('Erreur lors de la copie'))
}

function closeDisableA2FModal() {
  showDisableA2FModal.value = false
  disablePassword.value = ''
  disableOtp.value = ''
}

async function confirmDisableA2F() {
  try {
    const response = await fetch('/api/disable_a2f', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        password: disablePassword.value,
        otp: disableOtp.value
      }),
      credentials: 'include'
    })

    const data = await response.json()

    if (response.ok && data.status === 'success') {
      await status_a2f()
      showDisableA2FModal.value = false
      disablePassword.value = ''
      disableOtp.value = ''
    } else {
      alert('Mot de passe ou code incorrect')
    }
  } catch (error) {
    console.error('Erreur:', error)
    alert('Erreur de connexion')
  }
}

onMounted(() => {
  status_a2f();
})
</script>

<template>
  <div class="main-content">
    <h2 class="page-title">Paramètres du compte</h2>

    <div class="section">
      <h3 class="section-title">Mot de passe</h3>
      <div class="change-password-form">
        <div class="input-group">
          <label for="old-password">Ancien mot de passe</label>
          <input
            id="old-password"
            type="password"
            placeholder="Entrez votre mot de passe actuel"
          />
        </div>
        <div class="input-group">
          <label for="new-password">Nouveau mot de passe</label>
          <input
            id="new-password"
            type="password"
            placeholder="Entrez votre nouveau mot de passe"
          />
        </div>
        <div class="input-group">
          <label for="confirm-password">Confirmer le nouveau mot de passe</label>
          <input
            id="confirm-password"
            type="password"
            placeholder="Confirmez votre nouveau mot de passe"
          />
        </div>
        <button class="submit-btn">Changer le mot de passe</button>
      </div>
    </div>

    <div class="section">
      <h3 class="section-title">Authentification à double facteur</h3>
      <div class="a2f-container">
        <div class="a2f-info">
          <p class="a2f-status">
            Statut : <span class="status-badge" id="status_a2f"></span>
          </p>
        </div>
        <button class="action-btn" id="a2f_button" @click="check_password_a2f"> </button>
      </div>
    </div>

    <div class="section">
      <h3 class="section-title">Clé privée</h3>
      <div class="export-container">
        <p class="export-description">
          Sauvegardez votre clé privée pour pouvoir restaurer votre compte en cas de besoin.
        </p>
        <button class="export-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Sauvegarder ma clé privée
        </button>
      </div>
    </div>
  </div>

  <!-- Modal de vérification du mot de passe -->
  <div class="modal-password-a2f" v-if="showPasswordModal" @click="closePasswordModal">
    <div class="modal-content" @click.stop>
      <h3>Vérification du mot de passe</h3>
      <p>Entrez votre mot de passe pour activer l'authentification à double facteur</p>
      <input type="password" v-model="password" placeholder="Mot de passe" />
      <div class="modal-actions">
        <button class="cancel-btn" @click="closePasswordModal">Annuler</button>
        <button class="confirm-btn" @click="confirmPassword">Confirmer</button>
      </div>
    </div>
  </div>

  <!-- Modal d'activation A2F -->
  <div class="modal-password-a2f" v-if="showA2FModal" @click="closeA2FModal">
    <div class="modal-content modal-a2f" @click.stop>
      <h3>Activer l'authentification à double facteur</h3>
      <p>Scannez ce QR code avec votre application d'authentification (Google Authenticator, Authy, etc.)</p>

      <div class="qr-container">
        <img :src="qrCodeBase64" alt="QR Code" class="qr-code" />
      </div>

      <div class="secret-key">
        <label>Clé secrète (si vous ne pouvez pas scanner) :</label>
        <div class="key-container">
          <code>{{ secretKey }}</code>
          <button class="copy-btn" title="Copier" @click="copySecretKey">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 9H11C9.89543 9 9 9.89543 9 11V20C9 21.1046 9.89543 22 11 22H20C21.1046 22 22 21.1046 22 20V11C22 9.89543 21.1046 9 20 9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M5 15H4C3.46957 15 2.96086 14.7893 2.58579 14.4142C2.21071 14.0391 2 13.5304 2 13V4C2 3.46957 2.21071 2.96086 2.58579 2.58579C2.96086 2.21071 3.46957 2 4 2H13C13.5304 2 14.0391 2.21071 14.4142 2.58579C14.7893 2.96086 15 3.46957 15 4V5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="verification-code">
        <label>Entrez le code de vérification :</label>
        <input v-model="otpcode" type="text" placeholder="000000" maxlength="6" />
      </div>

      <div class="modal-actions">
        <button class="cancel-btn" @click="closeA2FModal">Annuler</button>
        <button class="confirm-btn" @click="confirmA2F">Activer l'A2F</button>
      </div>
    </div>
  </div>

  <!-- Modal de désactivation A2F -->
  <div class="modal-password-a2f" v-if="showDisableA2FModal" @click="closeDisableA2FModal">
    <div class="modal-content" @click.stop>
      <h3>Désactiver l'authentification à double facteur</h3>
      <div class="input-group">
        <label for="disable-password">Mot de passe</label>
        <input
          id="disable-password"
          v-model="disablePassword"
          type="password"
          placeholder="Votre mot de passe"
        />
      </div>

      <div class="input-group">
        <label for="disable-otp">Code de vérification</label>
        <input
          id="disable-otp"
          v-model="disableOtp"
          type="text"
          placeholder="000000"
          maxlength="6"
          style="text-align: center; letter-spacing: 8px; font-family: 'Courier New', monospace; font-size: 18px;"
        />
      </div>

      <div class="modal-actions">
        <button class="cancel-btn" @click="closeDisableA2FModal">Annuler</button>
        <button class="confirm-btn" @click="confirmDisableA2F">Désactiver l'A2F</button>
      </div>
    </div>
  </div>

</template>

<style scoped>
.main-content {
  display: flex;
  flex-direction: column;
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  gap: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 32px;
  border-bottom: 2px solid var(--border-input-color);
}

.section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0;
}

/* Password Section */
.change-password-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-hover-color);
}

.input-group input {
  padding: 12px 16px;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.input-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--secondary-color);
}

.input-group input::placeholder {
  color: #999;
}

.submit-btn {
  padding: 14px 24px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-start;
  margin-top: 4px;
}

.submit-btn:hover {
  background-color: var(--primary-hover-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.submit-btn:active {
  transform: translateY(0);
}

/* 2FA Section */
.a2f-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: #fafafa;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
  gap: 24px;
}

.a2f-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.a2f-description {
  font-size: 15px;
  color: var(--primary-hover-color);
  margin: 0;
  line-height: 1.5;
}

.a2f-status {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.status-badge.inactive {
  background-color: #fee;
  color: var(--red-warning);
}

.status-badge.active {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.action-btn {
  padding: 12px 24px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: 4px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.action-btn:active {
  transform: translateY(0);
}

/* Export Section */
.export-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.export-description {
  font-size: 15px;
  color: var(--primary-hover-color);
  margin: 0;
  line-height: 1.5;
}

.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 24px;
  border: none;
  background: var(--primary-color);
  cursor: pointer;
  color: white;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s ease;
  align-self: flex-start;
}

.export-btn:hover {
  background: var(--primary-hover-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.export-btn:active {
  transform: translateY(0);
}

.export-btn svg {
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .main-content {
    padding: 24px;
    gap: 24px;
  }

  .page-title {
    font-size: 24px;
  }

  .section-title {
    font-size: 18px;
  }

  .a2f-container {
    flex-direction: column;
    align-items: stretch;
  }

  .action-btn {
    width: 100%;
  }

  .submit-btn,
  .export-btn {
    width: 100%;
    justify-content: center;
  }
}


.modal-password-a2f {
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background-color: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-content h3 {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

.modal-content p {
  font-size: 15px;
  color: var(--primary-hover-color);
  margin: 0;
}

.modal-content input {
  padding: 12px 16px;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.modal-content input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--secondary-color);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn, .confirm-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: var(--primary-color);
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.confirm-btn {
  background-color: var(--primary-color);
  color: var(--secondary-color);
}

.confirm-btn:hover {
  background-color: var(--primary-hover-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Modal A2F spécifique */
.modal-a2f {
  max-width: 600px;
}

.qr-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
}

.qr-code {
  width: 200px;
  height: 200px;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
  background-color: white;
  padding: 10px;
}

.secret-key {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.secret-key label {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-hover-color);
}

.key-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: #fafafa;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
}

.key-container code {
  flex: 1;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: var(--primary-color);
  letter-spacing: 2px;
}

.copy-btn {
  padding: 6px;
  background-color: transparent;
  border: none;
  cursor: pointer;
  color: var(--primary-color);
  border-radius: 4px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.copy-btn:hover {
  background-color: var(--border-input-color);
}

.verification-code {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.verification-code label {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-hover-color);
}

.verification-code input {
  padding: 12px 16px;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
  font-size: 18px;
  text-align: center;
  letter-spacing: 8px;
  font-family: 'Courier New', monospace;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.verification-code input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--secondary-color);
}
</style>