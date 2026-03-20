import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import AboutView from '../views/AboutView.vue'
import FeedbackView from '../views/FeedbackView.vue'
import AdminView from '../views/AdminView.vue'
import BoardView from '../views/BoardView.vue'
import PostDetailView from '../views/PostDetailView.vue'
import PostWriteView from '../views/PostWriteView.vue'

const routes = [
  { path: '/', name: 'main', component: MainView },
  { path: '/about', name: 'about', component: AboutView },
  { path: '/feedback', name: 'feedback', component: FeedbackView },
  { path: '/admin', name: 'admin', component: AdminView },
  { path: '/board', name: 'board', component: BoardView },
  { path: '/board/write', name: 'postWrite', component: PostWriteView },
  { path: '/board/:id', name: 'postDetail', component: PostDetailView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
