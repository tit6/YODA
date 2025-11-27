<script setup lang="ts">

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
          <p class="a2f-description">
            Renforcez la sécurité de votre compte en activant l'authentification à deux facteurs.
          </p>
          <p class="a2f-status">
            Statut : <span class="status-badge inactive">Désactivée</span>
          </p>
        </div>
        <button class="action-btn">Activer</button>
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
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.action-btn:hover {
  background-color: var(--primary-hover-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
</style>