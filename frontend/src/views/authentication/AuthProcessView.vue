<script setup lang="ts">

</script>

<template>
  <div class="login-container">
    <div class="login-content">
      <div class="form-section">
        <router-view />
      </div>
      <div class="right-section">
        <div class="overlay">
          <h1 class="brand-title">YODA</h1>
          <p class="brand-subtitle">Votre coffre fort numérique.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}


.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-color);
  padding: 20px;
}

.login-content {
  display: flex;
  width: 100%;
  max-width: 1200px;
  min-height: 700px;
  max-height: 700px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* Left */
.form-section {
  flex: 1.2;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
}

/* Right side - Image */
.right-section {
  flex: 1;
  background: linear-gradient(135deg, #1a1a1a 0%, var(--primary-color) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.overlay {
  position: relative;
  z-index: 1;
  text-align: center;
  color: var(--secondary-color);
  padding: 40px;
}


/* Branding */
.brand-title {
  font-size: 64px;
  font-weight: 900;
  letter-spacing: 8px;
  margin-bottom: 16px;
  text-shadow: 2px 2px 20px rgba(255, 255, 255, 0.3);
}

.brand-subtitle {
  font-size: 18px;
  font-weight: 300;
  letter-spacing: 2px;
  opacity: 0.9;
}

</style>