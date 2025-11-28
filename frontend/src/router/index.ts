import { createRouter, createWebHistory } from 'vue-router'
import AuthProcessView from '../views/authentication/AuthProcessView.vue'
import LoginView from '../views/authentication/LoginView.vue'
import EmailValidationView from '../views/authentication/EmailValidationView.vue'
import Verify2FAView from '../views/authentication/Verify2FAView.vue'
import RecoveryCodesView from '../views/dashboard/account/RecoveryCodesView.vue'
import TestDb from '../views/testdb.vue'
import DashboardLayout from '../views/dashboard/DashboardLayout.vue'
import AdminDashboardView from '../views/dashboard/AdminDashboardView.vue'
import DocumentsView from '../views/dashboard/DocumentsView.vue'
import SharedDocumentsView from '../views/dashboard/SharedDocumentsView.vue'
import AccountView from '../views/dashboard/account/AccountView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
      {
          path: '/auth',
          component: AuthProcessView,
          meta: { requiresGuest: true },
          children: [
              {
                  path: '',
                  redirect: '/auth/login'
              },
              {
                  path: 'login',
                  name: 'login',
                  component: LoginView,
                  meta: { requiresGuest: true }
              },
              {
                  path: 'email-validation',
                  name: 'email-validation',
                  component: EmailValidationView,
                  meta: { requiresGuest: true }
              },
              {
                  path: 'verify-2fa',
                  name: 'verify-2fa',
                  component: Verify2FAView,
                  meta: { requiresGuest: true }
              }
          ]
      },
      {
          path: '/recovery-codes',
          name: 'recovery-codes',
          component: RecoveryCodesView
      },
      {
          path: '/',
          name: 'testdb',
          component: TestDb
      },
      {
          path: '/dashboard',
          name: 'dashboard',
          component: DashboardLayout,
          children: [
              {
                  path: '',
                  redirect: '/dashboard/documents'
              },
              {
                  path: 'admin',
                  name: 'dashboard-admin',
                  component: AdminDashboardView,
                  meta: { title: 'Administration' }
              },
              {
                  path: 'documents',
                  name: 'dashboard-documents',
                  component: DocumentsView,
                  meta: { title: 'Mes Documents' }
              },
              {
                  path: 'shared',
                  name: 'dashboard-shared',
                  component: SharedDocumentsView,
                  meta: { title: 'Partages' }
              },
              {
                  path: 'account',
                  name: 'dashboard-account',
                  component: AccountView,
                  meta: { title: 'Mon compte' }
              }
          ]
      }
  ],
})

router.beforeEach((to, from) => {
  const authStore = useAuthStore()

  // Si l'utilisateur a le 2FA à activer mais n'est pas sur la page de vérification
  if (authStore.requires_a2f && to.name !== 'verify-2fa') {
    return { name: 'verify-2fa' }
  }

  // Si l'utilisateur est authentifié et tente d'accéder à une route requiresGuest
  if (to.meta.requiresGuest && authStore.isAuthenticated && !authStore.requires_a2f) {
    return { name: 'dashboard-documents'}
  } else if (!to.meta.requiresGuest && !authStore.isAuthenticated) {
    return { name: 'login'}
  }

  return true
})

export default router
