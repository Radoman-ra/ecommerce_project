<template>
  <div class="login-page">
    <h1>Login</h1>
    <form @submit.prevent="login" class="login-form">
      <input v-model="email" placeholder="Email" required class="input-field" />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
        class="input-field"
      />
      <button type="submit" class="btn">Login</button>
      <div v-if="loginError" class="error">{{ loginError }}</div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import Cookies from 'js-cookie'

export default defineComponent({
  setup() {
    const email = ref('')
    const password = ref('')
    const loginError = ref('') // New ref for storing login errors
    const router = useRouter()

    const ACCESS_TOKEN_EXPIRE_MINUTES = 15
    const REFRESH_TOKEN_EXPIRE_DAYS = 7

    const login = async () => {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/auth/login', {
          email: email.value,
          password: password.value
        })

        const { access_token, refresh_token } = response.data

        Cookies.set('access_token', access_token, {
          expires: ACCESS_TOKEN_EXPIRE_MINUTES / (24 * 60),
          secure: true
        })

        Cookies.set('refresh_token', refresh_token, {
          expires: REFRESH_TOKEN_EXPIRE_DAYS,
          secure: true
        })

        router.push('/')
      } catch (error) {
        // Handle the error here
        if ((error as any).response && (error as any).response.status === 401) {
          loginError.value = 'Invalid email or password.' // Set error message for 401 status
        } else {
          loginError.value = 'An error occurred. Please try again.' // General error message
        }
        console.error('Login failed:', error)
      }
    }

    return {
      email,
      password,
      login,
      loginError // Return the loginError ref for template binding
    }
  }
})
</script>

<style scoped>
.login-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: #fff;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
}

.input-field {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 15px;
  width: 200px;
}

.btn {
  padding: 10px 20px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #d8e2dc;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
