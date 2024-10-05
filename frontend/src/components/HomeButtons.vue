<template>
  <div class="auth-buttons">
    <button v-if="isAuthenticated" @click="logout" class="btn">Logout</button>
    <button v-if="!isAuthenticated" @click="goToLogin" class="btn">Login</button>
    <button v-if="!isAuthenticated" @click="goToRegister" class="btn">Register</button>
    <button v-else @click="goToProfile" class="btn">Profile</button>
    <button @click="goToCart" class="btn">Cart</button>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'
import Cookies from 'js-cookie'

export default defineComponent({
  setup() {
    const router = useRouter()

    const isAuthenticated = !!Cookies.get('access_token')

    const goToLogin = () => router.push('/login')
    const goToRegister = () => router.push('/register')
    const goToProfile = () => router.push('/profile')
    const goToCart = () => router.push('/cart')

    const logout = () => {
      Cookies.remove('access_token')
      Cookies.remove('refresh_token')
      location.reload()
    }

    return {
      isAuthenticated,
      goToLogin,
      goToRegister,
      goToProfile,
      goToCart,
      logout
    }
  }
})
</script>

<style scoped>
.auth-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 20px;
  color: #333;
  font-size: 16px;
  cursor: pointer;
  transition:
    background-color 0.3s,
    color 0.3s;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
}

.btn:hover {
  background-color: #d8e2dc;
  color: #000;
}
</style>
