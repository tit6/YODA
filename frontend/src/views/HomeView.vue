<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const featureCards = [
  {
    title: 'Chiffrement bout en bout',
    description: 'Vos fichiers sont protégés par AES-256 et des clés uniques avant même de quitter votre poste.',
    tag: 'Sécurité avancée'
  },
  {
    title: 'Partage maîtrisé',
    description: 'Invitations temporaires, liens chiffrés et suivi des accès pour collaborer sans perdre le contrôle.',
    tag: 'Collaboration'
  },
  {
    title: 'Traçabilité totale',
    description: 'Chaque action est historisée pour vous offrir une piste d’audit claire et exploitable.',
    tag: 'Conformité'
  }
]

const highlights = [
  { label: 'Déploiement', value: '< 10 min', detail: 'Depuis votre infrastructure ou notre cloud privé.' },
  { label: 'Disponibilité', value: '99.9 %', detail: 'Plateforme monitorée en continu et tolérante aux pannes.' },
  { label: 'Cybersécurité', value: 'SOC & ISO', detail: 'Aligné sur les bonnes pratiques RGPD et SecNumCloud.' }
]

const goToLogin = () => {
  router.push({ name: 'login' })
}

const scrollToFeatures = () => {
  const target = document.getElementById('features')
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>

<template>
  <div class="landing-page">
    <section class="hero-section">
      <div class="hero-content">
        <p class="eyebrow">Coffre-fort numérique souverain</p>
        <h1>Centralisez, chiffrez et partagez vos documents sensibles en toute confiance.</h1>
        <p class="subtitle">
          YODA combine chiffrement zero-knowledge, authentification multifacteur et gouvernance fine des accès pour
          accélérer vos projets sans sacrifier la sécurité.
        </p>
        <div class="cta-group">
          <button class="btn primary" @click="goToLogin">
            Commencer maintenant
          </button>
          <button class="btn ghost" @click="scrollToFeatures">
            Voir les fonctionnalités
          </button>
        </div>
        <div class="hero-badges">
          <div class="badge">
            <span class="badge-title">2FA obligatoire</span>
            <p>Protection native par mot de passe robuste + TOTP.</p>
          </div>
          <div class="badge">
            <span class="badge-title">Stockage souverain</span>
            <p>Données hébergées en France et récupérables à tout moment.</p>
          </div>
        </div>
      </div>
      <div class="hero-visual">
        <div class="floating-card main-card">
          <h3>YODA Vault</h3>
          <ul>
            <li>
              <span class="dot green"></span>
              Chiffrement actif
            </li>
            <li>
              <span class="dot blue"></span>
              Liens temporaires
            </li>
            <li>
              <span class="dot purple"></span>
              Journalisation 24/7
            </li>
          </ul>
        </div>
        <div class="floating-card stats-card">
          <p class="card-label">Activité</p>
          <h4>98 opérations validées</h4>
          <p class="card-caption">Accès conformes au protocole interne.</p>
        </div>
      </div>
    </section>

    <section id="features" class="features-section">
      <header>
        <p class="eyebrow">Pourquoi YODA ?</p>
        <h2>Une plateforme pensée pour les équipes qui manipulent des données critiques.</h2>
      </header>
      <div class="features-grid">
        <article
          v-for="feature in featureCards"
          :key="feature.title"
          class="feature-card"
        >
          <span class="feature-tag">{{ feature.tag }}</span>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </article>
      </div>
    </section>

    <section class="metrics-section">
      <div class="metrics-grid">
        <article
          v-for="metric in highlights"
          :key="metric.label"
          class="metric-card"
        >
          <p class="metric-label">{{ metric.label }}</p>
          <p class="metric-value">{{ metric.value }}</p>
          <p class="metric-detail">{{ metric.detail }}</p>
        </article>
      </div>
      <div class="metrics-description">
        <h2>Un socle technique mature, connecté à vos outils.</h2>
        <p>
          Connectez YODA à votre SSO, automatisez les imports depuis vos référentiels internes et surveillez la santé
          de la plateforme depuis vos propres outils d’observabilité.
        </p>
        <ul>
          <li>API documentée et stable pour intégrer vos workflows.</li>
          <li>Logs exportables pour vos SIEM et centres de supervision.</li>
          <li>Support entreprise avec engagements de service clairs.</li>
        </ul>
      </div>
    </section>

    <section class="final-cta">
      <div class="cta-card">
        <div>
          <p class="eyebrow">Prêt à sécuriser vos données ?</p>
          <h2>Déployez YODA aujourd’hui et offrez une expérience moderne à vos équipes.</h2>
        </div>
        <button class="btn primary" @click="goToLogin">
          Accéder à la plateforme
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.landing-page {
  min-height: 100vh;
  width: 100%;
  background: radial-gradient(circle at top, rgba(255, 255, 255, 0.05), transparent 50%), #050505;
  color: var(--secondary-color);
  padding: 0 24px 96px;
}

.hero-section {
  display: flex;
  flex-wrap: wrap;
  gap: 40px;
  padding: 120px 0 80px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-content {
  flex: 1 1 460px;
  max-width: 640px;
}

.hero-content h1 {
  font-size: clamp(2.5rem, 5vw, 3.7rem);
  line-height: 1.1;
  margin-bottom: 24px;
  font-weight: 700;
}

.subtitle {
  color: rgba(255, 255, 255, 0.75);
  font-size: 1.1rem;
  line-height: 1.5;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 0.85rem;
  color: var(--primary-active-color);
  margin-bottom: 16px;
  display: inline-block;
}

.cta-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin: 32px 0;
}

.btn {
  border: 1px solid transparent;
  padding: 14px 28px;
  font-size: 1rem;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease;
  font-weight: 600;
}

.btn.primary {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover-color));
  color: var(--secondary-color);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
}

.btn.primary:hover {
  transform: translateY(-2px);
}

.btn.ghost {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.3);
  color: var(--secondary-color);
}

.btn.ghost:hover {
  border-color: var(--secondary-color);
}

.hero-badges {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 32px;
}

.badge {
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.badge-title {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
}

.hero-visual {
  flex: 1 1 320px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.floating-card {
  backdrop-filter: blur(16px);
  background: rgba(10, 10, 10, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 28px;
  color: var(--secondary-color);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
}

.main-card {
  width: 320px;
  align-self: flex-start;
}

.main-card ul {
  list-style: none;
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0;
}

.main-card li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.dot.green {
  background: #3dd598;
}

.dot.blue {
  background: #0096ff;
}

.dot.purple {
  background: #8b5cf6;
}

.stats-card {
  position: absolute;
  right: 10%;
  bottom: 0;
  transform: translateY(40px);
}

.card-label {
  text-transform: uppercase;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 0.2em;
  margin-bottom: 8px;
}

.card-caption {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-top: 8px;
}

.features-section {
  padding: 80px 0;
}

.features-section header {
  max-width: 720px;
  margin-bottom: 40px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 28px;
  min-height: 220px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: transform 0.2s ease, border 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.2);
}

.feature-tag {
  font-size: 0.75rem;
  color: var(--primary-active-color);
  text-transform: uppercase;
  letter-spacing: 0.2em;
}

.metrics-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 32px;
  padding: 64px 0;
  align-items: center;
}

.metrics-grid {
  display: grid;
  gap: 18px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 24px;
}

.metric-label {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.6);
}

.metric-value {
  font-size: 2.1rem;
  font-weight: 700;
  margin: 8px 0;
}

.metric-detail {
  color: rgba(255, 255, 255, 0.65);
}

.metrics-description h2 {
  font-size: 2rem;
  margin-bottom: 16px;
}

.metrics-description p {
  color: rgba(255, 255, 255, 0.75);
  margin-bottom: 16px;
}

.metrics-description ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metrics-description li::before {
  content: '•';
  margin-right: 8px;
  color: var(--primary-active-color);
}

.final-cta {
  padding-top: 40px;
}

.cta-card {
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(34, 34, 34, 0.9));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 28px;
  padding: 40px;
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  align-items: center;
  justify-content: space-between;
}

.cta-card h2 {
  max-width: 580px;
}

@media (max-width: 768px) {
  .hero-section {
    padding-top: 80px;
  }

  .hero-visual {
    order: -1;
  }

  .cta-card {
    flex-direction: column;
    text-align: center;
  }

  .stats-card {
    position: relative;
    right: auto;
    bottom: auto;
    transform: translateY(0);
    margin-top: 24px;
  }
}
</style>
