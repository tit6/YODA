<script setup lang="ts">

</script>

<template>
  <div class="main-content">

    <div class="section">
      <h4>Mots de passe</h4>
      <div class="change-password-form">
        <input type="password" placeholder="Ancien mot de passe" />
        <input type="password" placeholder="Nouveau mot de passe" />
        <input type="password" placeholder="Confirmer le nouveau mot de passe" />
        <button>Changer le mot de passe</button>
      </div>
    </div>

    <div class="section">
      <h4>Authentification à double facteur</h4>
      <div class="a2f-form">
        <p>Activer/Desactiver</p>
        <button>Activer</button>
      </div>
    </div>

    <button class="export-btn">
      Sauvegarder ma clé privée
    </button>
  </div>
</template>

<style scoped>
.main-content {
  display: flex;
  flex-direction: column;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  gap: 24px;
}

.change-password-form{
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.a2f-form{
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 5vh;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
  align-items: center;
  gap: 12px;
}

.export-btn{
  width: 15%;
  border: none;
  background: var(--primary-color);
  cursor: pointer;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
}

.export-btn:hover{
  background: var(--primary-hover-color);
}
</style>