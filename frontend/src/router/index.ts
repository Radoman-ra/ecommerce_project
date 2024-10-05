import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/HomePage.vue'
import Login from '../pages/LoginPage.vue'
import Register from '../pages/RegisterPage.vue'
import Cart from '../pages/CartPage.vue'
import Profile from '../pages/ProfilePage.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/cart', component: Cart },
  { path: '/profile', component: Profile }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
