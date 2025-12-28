<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import IconDocument from '@/views/assets/icons/IconDocument.vue'
import IconShare from '@/views/assets/icons/IconShare.vue'
import IconSecurity from '@/views/assets/icons/IconSecurity.vue'
import IconChevronLeft from '@/views/assets/icons/IconChevronLeft.vue'
import IconLogout from '@/views/assets/icons/IconLogout.vue'
import IconChevronDown from '@/views/assets/icons/IconChevronDown.vue'

const authStore = useAuthStore()

const router = useRouter()
const route = useRoute()

const userName = ref('Jean Dupont')
const userEmail = computed(() => authStore.email)

const isSidebarCollapsed = ref(false)
const showUserMenu = ref(false)

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const logout = () => {
  authStore.logout()
  router.push('login')
}

const isActive = (routePath: string) => {
  return route.path === routePath
}

async function fetchUserName() {
  try {
    const response = await fetch('/api/name_user', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      credentials: 'include'
    })

    const data = await response.json()

    if (response.ok && data.status === 'success') {
      userName.value = `${data.prenom} ${data.nom}`
    }
  } catch (error) {
    console.error('Erreur lors de la récupération du nom:', error)
  }
}

onMounted(() => {
  fetchUserName()
})
</script>

<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-text" v-if="!isSidebarCollapsed">YODA</span>
          <span class="logo-icon" v-else>Y</span>
        </div>
      </div>
      <nav class="sidebar-nav">

        <!-- DOCUMENTS -->
        <router-link
          to="/dashboard/documents"
          class="nav-item"
          :class="{ active: isActive('/dashboard/documents') }"
        >
          <IconDocument class="nav-icon" />
          <span class="nav-label" v-if="!isSidebarCollapsed">Mes Documents</span>
        </router-link>

        <!-- PARTAGES -->
        <router-link
          to="/dashboard/shared"
          class="nav-item"
          :class="{ active: isActive('/dashboard/shared') }"
        >
          <IconShare class="nav-icon" />
          <span class="nav-label" v-if="!isSidebarCollapsed">Partages</span>
        </router-link>

        <!-- SÉCURITÉ -->
        <router-link
          to="/dashboard/account"
          class="nav-item"
          :class="{ active: isActive('/dashboard/account') }"
        >
          <IconSecurity class="nav-icon" />
          <span class="nav-label" v-if="!isSidebarCollapsed">Mon compte</span>
        </router-link>

      </nav>

      <div class="sidebar-footer">
        <button @click="toggleSidebar" class="collapse-btn">
          <IconChevronLeft />
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="main-container">
      <!-- Top Header -->
      <header class="top-header">
        <div class="header-left">
          <h1 class="page-title">{{ route.meta.title }}</h1>
        </div>

        <div class="header-right">
          <!-- User Menu -->
          <div class="user-menu" @click="showUserMenu = !showUserMenu">
            <div class="user-avatar">
              {{ userName.charAt(0) }}
            </div>
            <div class="user-info" v-if="!isSidebarCollapsed">
              <span class="user-name">{{ userName }}</span>
              <span class="user-role">Utilisateur</span>
            </div>
            <IconChevronDown class="chevron" />

            <!-- Dropdown -->
            <div class="user-dropdown" v-if="showUserMenu">
              <div class="dropdown-header">
                <p class="dropdown-name">{{ userName }}</p>
                <p class="dropdown-email">{{ userEmail }}</p>
              </div>
              <div class="dropdown-divider"></div>
              <button @click="logout" class="dropdown-item danger">
                <IconLogout />
                Déconnexion
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-page);
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-width);
  background-color: var(--sidebar-bg);
  color: var(--secondary-color);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-base);
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  z-index: var(--z-modal);
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  padding: var(--space-xl);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-extrabold);
  letter-spacing: 4px;
}

.logo-icon {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-extrabold);
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-xl) 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: 14px var(--space-xl);
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all var(--transition-base);
  position: relative;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--secondary-color);
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--secondary-color);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background-color: var(--secondary-color);
}

.nav-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.nav-label {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 14px;
}

.sidebar-footer {
  padding: var(--space-lg);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.collapse-btn {
  width: 100%;
  padding: var(--space-md);
  background-color: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: var(--border-radius-md);
  color: var(--secondary-color);
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.collapse-btn svg {
  width: 20px;
  height: 20px;
  transition: transform var(--transition-base);
}

.sidebar.collapsed .collapse-btn svg {
  transform: rotate(180deg);
}

/* Main Container */
.main-container {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  transition: margin-left var(--transition-base);
}

.sidebar.collapsed ~ .main-container {
  margin-left: var(--sidebar-collapsed-width);
}

/* Top Header */
.top-header {
  height: var(--header-height);
  background-color: var(--secondary-color);
  border-bottom: var(--border-width) solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xxl);
  position: sticky;
  top: 0;
  z-index: var(--z-dropdown);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-xl);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-md);
  background-color: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  transition: all var(--transition-base);
  position: relative;
}

.icon-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.icon-btn svg {
  width: 22px;
  height: 22px;
}

.badge {
  position: absolute;
  top: var(--space-xs);
  right: var(--space-xs);
  background-color: var(--color-danger);
  color: var(--secondary-color);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

/* User Menu */
.user-menu {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
}

.user-menu:hover {
  background-color: var(--bg-hover);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover-color) 100%);
  color: var(--secondary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-lg);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.user-role {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.chevron {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
}

.user-dropdown {
  position: absolute;
  top: calc(100% + var(--space-sm));
  right: 0;
  width: 280px;
  background-color: var(--bg-card);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  z-index: var(--z-modal);
}

.dropdown-header {
  padding: var(--space-lg);
  background-color: var(--bg-input-disabled);
}

.dropdown-name {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.dropdown-email {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--border-color);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  color: var(--text-primary);
  text-decoration: none;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: var(--font-size-base);
}

.dropdown-item:hover {
  background-color: var(--bg-input-disabled);
}

.dropdown-item svg {
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.dropdown-item.danger {
  color: var(--color-danger);
}

.dropdown-item.danger svg {
  color: var(--color-danger);
}

/* Main Content */
.main-content {
  flex: 1;
  padding: var(--space-xxl);
  overflow-y: auto;
}

@media (max-width: 768px) {
  .sidebar {
    width: var(--sidebar-collapsed-width);
  }

  .sidebar .nav-label,
  .sidebar .user-info {
    display: none;
  }

  .main-container {
    margin-left: var(--sidebar-collapsed-width);
  }
}
</style>
