<template>
  <div class="register-page">
    <h2>Register</h2>
    <form @submit.prevent="register" class="register-form">
      <input v-model="username" placeholder="Username" required class="input-field" />
      <input v-model="email" placeholder="Email" type="email" required class="input-field" />
      <input
        v-model="password"
        placeholder="Password"
        type="password"
        required
        class="input-field"
      />
      <button type="submit" class="btn">Register</button>
    </form>
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
  background-color: #f0f0f0;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #d8e2dc;
}
</style>
