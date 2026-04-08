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
import VenueWriteView from '../views/venues/VenueWriteView.vue'
import EventWriteView from '../views/events/EventWriteView.vue'
import EventListView from '../views/events/EventListView.vue'
import VenueListView from '../views/venues/VenueListView.vue'
import BookmarkView from '../views/BookmarkView.vue'
import SocialCallbackView from '../views/SocialCallbackView.vue'
import SocialRegisterView from '../views/SocialRegisterView.vue'

const routes = [
  { path: '/', name: 'main', component: MainView },
  { path: '/about', name: 'about', component: AboutView },
  { path: '/feedback', name: 'feedback', component: FeedbackView },
  { path: '/admin', name: 'admin', component: AdminView },
  { path: '/board', name: 'board', component: BoardView },
  { path: '/board/write', name: 'postWrite', component: PostWriteView },
  { path: '/board/:id', name: 'postDetail', component: PostDetailView },
  { path: '/events', name: 'eventList', component: EventListView },
  { path: '/venues', name: 'venueList', component: VenueListView },
  { path: '/events/new', name: 'eventNew', component: EventWriteView },
  { path: '/events/:id/edit', name: 'eventEdit', component: EventWriteView },  
  { path: '/events/:id', name: 'eventDetail', component: EventDetailView },
  { path: '/venues/new', name: 'venueNew', component: VenueWriteView },
  { path: '/venues/:id/edit', name: 'venueEdit', component: VenueWriteView },
  { path: '/venues/:id', name: 'venueDetail', component: VenueDetailView },
  { path: '/bookmarks', name: 'bookmarks', component: BookmarkView },
  { path: '/auth/:provider/callback', name: 'socialCallback', component: SocialCallbackView },
  { path: '/auth/social/register', name: 'socialRegister', component: SocialRegisterView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
