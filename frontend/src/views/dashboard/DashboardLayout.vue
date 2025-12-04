<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
          <svg class="nav-icon" viewBox="0 0 24 24">
            <path
              d="M9 12H15M9 16H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543
                 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L18.7071
                 8.70711C18.8946 8.89464 19 9.149 19 9.41421V19C19 20.1046 18.1046 21 17
                 21Z"
              fill="currentColor"
            />
          </svg>
          <span class="nav-label" v-if="!isSidebarCollapsed">Mes Documents</span>
        </router-link>

        <!-- PARTAGES -->
        <router-link
          to="/dashboard/shared"
          class="nav-item"
          :class="{ active: isActive('/dashboard/shared') }"
        >
          <svg class="nav-icon" viewBox="0 0 24 24">
            <path
              d="M8.68387 13.3419C7.26266 12.6212 6 11.0738 6 9C6 6.23858 8.23858 4 11
                4C13.7614 4 16 6.23858 16 9C16 11.0738 14.7373 12.6212 13.3161
                13.3419C16.124 14.0988 18 16.2468 18 19H4C4 16.2468 5.87597 14.0988
                8.68387 13.3419Z M14 9C14 7.34315 12.6569 6 11 6C9.34315 6 8 7.34315 8
                9C8 10.6569 9.34315 12 11 12C12.6569 12 14 10.6569 14 9Z M18 9C18
                8.44772 18.4477 8 19 8C19.5523 8 20 8.44772 20 9V11H22C22.5523 11 23
                11.4477 23 12C23 12.5523 22.5523 13 22 13H20V15C20 15.5523 19.5523 16
                19 16C18.4477 16 18 15.5523 18 15V13H16C15.4477 13 15 12.5523 15
                12C15 11.4477 15.4477 11 16 11H18V9Z"
              fill="currentColor"
            />
          </svg>
          <span class="nav-label" v-if="!isSidebarCollapsed">Partages</span>
        </router-link>

        <!-- SÉCURITÉ -->
        <router-link
          to="/dashboard/account"
          class="nav-item"
          :class="{ active: isActive('/dashboard/account') }"
        >
          <svg class="nav-icon" viewBox="0 0 24 24">
            <path
              d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21
                11V5L12 1ZM12 11.99H19C18.47 16.11 15.72 19.78 12 20.93V12H5V6.3L12
                3.19V11.99Z"
              fill="currentColor"
            />
          </svg>
          <span class="nav-label" v-if="!isSidebarCollapsed">Mon compte</span>
        </router-link>

      </nav>

      <div class="sidebar-footer">
        <button @click="toggleSidebar" class="collapse-btn">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15.41 7.41L14 6L8 12L14 18L15.41 16.59L10.83 12L15.41 7.41Z" fill="currentColor"/>
          </svg>
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
            <svg class="chevron" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 10L12 15L17 10H7Z" fill="currentColor"/>
            </svg>

            <!-- Dropdown -->
            <div class="user-dropdown" v-if="showUserMenu">
              <div class="dropdown-header">
                <p class="dropdown-name">{{ userName }}</p>
                <p class="dropdown-email">{{ userEmail }}</p>
              </div>
              <div class="dropdown-divider"></div>
              <button @click="logout" class="dropdown-item danger">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M17 7L15.59 8.41L18.17 11H8V13H18.17L15.59 15.59L17 17L22 12L17 7ZM4 5H12V3H4C2.9 3 2 3.9 2 5V19C2 20.1 2.9 21 4 21H12V19H4V5Z" fill="currentColor"/>
                </svg>
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
  background-color: #f5f5f5;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  z-index: 1000;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 28px;
  font-weight: 900;
  letter-spacing: 4px;
}

.logo-icon {
  font-size: 28px;
  font-weight: 900;
}

.sidebar-nav {
  flex: 1;
  padding: 24px 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 24px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s ease;
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
  font-size: 15px;
  font-weight: 500;
  white-space: nowrap;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 14px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.collapse-btn {
  width: 100%;
  padding: 12px;
  background-color: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 8px;
  color: var(--secondary-color);
  cursor: pointer;
  transition: all 0.3s ease;
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
  transition: transform 0.3s ease;
}

.sidebar.collapsed .collapse-btn svg {
  transform: rotate(180deg);
}

/* Main Container */
.main-container {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}

.sidebar.collapsed ~ .main-container {
  margin-left: 80px;
}

/* Top Header */
.top-header {
  height: 70px;
  background-color: var(--secondary-color);
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-active-color);
  transition: all 0.3s ease;
  position: relative;
}

.icon-btn:hover {
  background-color: #f5f5f5;
  color: var(--primary-color);
}

.icon-btn svg {
  width: 22px;
  height: 22px;
}

.badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background-color: var(--red-warning);
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

/* User Menu */
.user-menu {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.user-menu:hover {
  background-color: #f5f5f5;
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
  font-weight: 700;
  font-size: 16px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
}

.user-role {
  font-size: 12px;
  color: var(--primary-active-color);
}

.chevron {
  width: 16px;
  height: 16px;
  color: var(--primary-active-color);
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 280px;
  background-color: var(--secondary-color);
  border-radius: 8px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 1000;
}

.dropdown-header {
  padding: 16px;
  background-color: #f8f9fa;
}

.dropdown-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.dropdown-email {
  font-size: 13px;
  color: var(--primary-active-color);
}

.dropdown-divider {
  height: 1px;
  background-color: #e5e5e5;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: var(--primary-color);
  text-decoration: none;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.dropdown-item svg {
  width: 18px;
  height: 18px;
  color: var(--primary-active-color);
}

.dropdown-item.danger {
  color: var(--red-warning);
}

.dropdown-item.danger svg {
  color: var(--red-warning);
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .sidebar {
    width: 80px;
  }

  .sidebar .nav-label,
  .sidebar .user-info {
    display: none;
  }

  .main-container {
    margin-left: 80px;
  }
}
</style>
