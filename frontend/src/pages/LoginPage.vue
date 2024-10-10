<template>
  <div class="login-page">
    <form @submit.prevent="login" class="login-form">
      <div class="login-text">Login</div>

      <input
        v-model="email"
        placeholder="Email"
        required
        class="input-field"
        :class="{ 'input-error': emailError }"
      />
      <div v-if="emailError" class="error-message">{{ emailError }}</div>

      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
        class="input-field"
        :class="{ 'input-error': passwordError }"
      />
      <div v-if="passwordError" class="error-message">{{ passwordError }}</div>

      <button type="submit" class="btn btn-login" :disabled="isSubmitting">Login</button>
      <button type="button" class="btn btn-register" @click="goToRegister">Register</button>

      <transition name="fade">
        <div v-if="loginError" class="login-error">{{ loginError }}</div>
      </transition>
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
    const emailError = ref('')
    const passwordError = ref('')
    const loginError = ref('')
    const isSubmitting = ref(false)
    const router = useRouter()

    const ACCESS_TOKEN_EXPIRE_MINUTES = 15
    const REFRESH_TOKEN_EXPIRE_DAYS = 7

    const validateInputs = (): boolean => {
      emailError.value = ''
      passwordError.value = ''

      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      let isValid = true

      if (!emailPattern.test(email.value)) {
        emailError.value = 'Please enter a valid email.'
        isValid = false
      }

      if (password.value.length < 6) {
        passwordError.value = 'Password must be at least 6 characters long.'
        isValid = false
      }

      return isValid
    }

    const login = async () => {
      if (!validateInputs()) return

      isSubmitting.value = true
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
        if ((error as any).response && (error as any).response.status === 401) {
          loginError.value = 'Invalid email or password.'
        } else {
          loginError.value = 'An error occurred. Please try again.'
        }
        console.error('Login failed:', error)
      } finally {
        isSubmitting.value = false
      }
    }

    const goToRegister = () => {
      router.push('/register')
    }

    return {
      email,
      password,
      emailError,
      passwordError,
      login,
      goToRegister,
      loginError,
      isSubmitting
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
  max-width: 220px;
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

.input-error {
  border-color: #dc3545;
}

.error-message {
  color: #dc3545;
  font-size: 0.85rem;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-login {
  background-color: #007bff;
  color: white;
}

.btn-login:disabled {
  background-color: #c0c0c0;
  cursor: not-allowed;
}

.btn-login:hover:enabled {
  background-color: #0056b3;
}

.btn-register {
  background-color: #6c757d;
  color: white;
}

.btn-register:hover {
  background-color: #5a6268;
}

.login-error {
  background-color: #dc3545;
  color: white;
  padding: 10px;
  border-radius: 10px;
  margin-top: 10px;
  text-align: center;
  font-weight: bold;
  animation: fade-in 0.5s;
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
