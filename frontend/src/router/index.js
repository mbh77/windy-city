import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import AboutView from '../views/AboutView.vue'

const routes = [
  { path: '/', name: 'main', component: MainView },
  { path: '/about', name: 'about', component: AboutView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
