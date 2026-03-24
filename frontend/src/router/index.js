import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import AboutView from '../views/AboutView.vue'
import FeedbackView from '../views/FeedbackView.vue'
import AdminView from '../views/AdminView.vue'
import BoardView from '../views/board/BoardView.vue'
import PostDetailView from '../views/board/PostDetailView.vue'
import PostWriteView from '../views/board/PostWriteView.vue'
import EventDetailView from '../views/events/EventDetailView.vue'
import VenueDetailView from '../views/venues/VenueDetailView.vue'
import EventWriteView from '../views/events/EventWriteView.vue'

const routes = [
  { path: '/', name: 'main', component: MainView },
  { path: '/about', name: 'about', component: AboutView },
  { path: '/feedback', name: 'feedback', component: FeedbackView },
  { path: '/admin', name: 'admin', component: AdminView },
  { path: '/board', name: 'board', component: BoardView },
  { path: '/board/write', name: 'postWrite', component: PostWriteView },
  { path: '/board/:id', name: 'postDetail', component: PostDetailView },
  { path: '/events/new', name: 'eventNew', component: EventWriteView },
  { path: '/events/:id/edit', name: 'eventEdit', component: EventWriteView },  
  { path: '/events/:id', name: 'eventDetail', component: EventDetailView },
  { path: '/venues/:id', name: 'venueDetail', component: VenueDetailView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
