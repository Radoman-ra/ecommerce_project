<template>
  <div class="auth-buttons">
    <img src="../icon/logo.svg" @click="home" alt="Logo" class="logo" />
    <button v-if="isAuthenticated" @click="logout" class="btn">Logout</button>
    <button v-if="!isAuthenticated" @click="goToLogin" class="btn">Login</button>
    <button v-if="!isAuthenticated" @click="goToRegister" class="btn">Register</button>
    <button v-else @click="goToProfile" class="btn">Profile</button>
    <button v-if="isAuthenticated" @click="goToCart" class="btn">Cart</button>
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

    const home = () => router.push('/')
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
      home,
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
  width: 100%;
  display: flex;
  padding: 10px;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: center;
}

.btn {
  padding: 10px 20px;
  background-color: #007bff;
  border-radius: 5px;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  outline: none;
  border: none;
}

.btn:hover {
  background-color: #0056b3;
}

.logo {
  width: 50px;
  height: 50px;
  margin-right: auto;
}
</style>
