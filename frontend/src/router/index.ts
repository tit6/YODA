import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import TestDb from '../views/testdb.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
      {
          path: '/login',
          name: 'login',
          component: LoginView
      },
      {
          path: '/',
          name: 'testdb',
          component: TestDb
      }
  ],
})

export default router
