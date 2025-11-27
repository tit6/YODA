import { createRouter, createWebHistory } from 'vue-router'
import AuthProcessView from '../views/authentication/AuthProcessView.vue'
import LoginView from '../views/authentication/LoginView.vue'
import EmailValidationView from '../views/authentication/EmailValidationView.vue'
import Setup2FAView from '../views/dashboard/account/Setup2FAView.vue'
import Verify2FAView from '../views/authentication/Verify2FAView.vue'
import RecoveryCodesView from '../views/dashboard/account/RecoveryCodesView.vue'
import TestDb from '../views/testdb.vue'
import DashboardLayout from '../views/dashboard/DashboardLayout.vue'
import AdminDashboardView from '../views/dashboard/AdminDashboardView.vue'
import DocumentsView from '../views/dashboard/DocumentsView.vue'
import SharedDocumentsView from '../views/dashboard/SharedDocumentsView.vue'
import AccountView from '../views/dashboard/account/AccountView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
      {
          path: '/auth',
          component: AuthProcessView,
          children: [
              {
                  path: 'login',
                  name: 'login',
                  component: LoginView
              },
              {
                  path: 'email-validation',
                  name: 'email-validation',
                  component: EmailValidationView
              },
              {
                  path: 'verify-2fa',
                  name: 'verify-2fa',
                  component: Verify2FAView
              }
          ]
      },
      {
          path: '/setup-2fa',
          name: 'setup-2fa',
          component: Setup2FAView
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
                  name: 'dashboard-document',
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

export default router
