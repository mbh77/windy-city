import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/styles/base.css'
import './assets/styles/layout.css'
import './assets/styles/topbar.css'
import './assets/styles/sidebar.css'
import './assets/styles/map.css'
import './assets/styles/modal.css'
import './assets/styles/form.css'
import './assets/styles/badges.css'
import './assets/styles/markdown.css'

createApp(App).use(router).mount('#app')
