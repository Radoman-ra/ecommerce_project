<template>
  <div class="register-page">
    <form @submit.prevent="register" class="register-form">
      <h2 class="register-text">Register</h2>
      <input v-model="username" placeholder="Username" required class="input-field" />
      <input v-model="email" placeholder="Email" type="email" required class="input-field" />
      <input
        v-model="password"
        placeholder="Password"
        type="password"
        required
        class="input-field"
      />
      <button type="submit" class="btn btn-primary">Register</button>
      <button @click="goToLogin" class="btn btn-secondary">Go to Login</button>
    </form>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default defineComponent({
  data() {
    return {
      username: '',
      email: '',
      password: '',
      message: ''
    }
  },
  setup() {
    const router = useRouter()
    return { router }
  },
  methods: {
    async register() {
      try {
        await axios.post('http://127.0.0.1:8000/api/auth/register', {
          username: this.username,
          email: this.email,
          password: this.password
        })

        this.message = 'Registration successful!'
        this.router.push('/login')
      } catch (error) {
        const err = error as any
        if (err.response) {
          if (err.response.status === 422 && Array.isArray(err.response.data.detail)) {
            this.message = err.response.data.detail.map((err: any) => err.msg).join(', ')
          } else if (err.response.data.detail && typeof err.response.data.detail === 'string') {
            this.message = err.response.data.detail
          } else {
            this.message = `Error: ${err.response.status} - ${err.response.data.detail || 'Unknown error'}`
          }
        } else {
          this.message = 'An error occurred. Please check your network connection.'
        }
      }
    },
    goToLogin() {
      this.router.push('/login')
    }
  }
})
</script>

<style scoped>
.register-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.register-form {
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
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.register-text {
  font-size: 24px;
  font-weight: 500;
}
</style>
