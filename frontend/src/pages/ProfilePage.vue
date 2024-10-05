<template>
  <div class="profile-wrapper">
    <div class="profile-container">
      <button class="home-button" @click="goHome">Home</button>
      <h1>My Orders</h1>
      <form class="filter-form" @submit.prevent="fetchOrders">
        <label for="status">Order Status:</label>
        <select v-model="selectedStatus" class="rounded-input">
          <option value="">All</option>
          <option value="Pending">Pending</option>
          <option value="Delivered">Delivered</option>
          <option value="Cancelled">Cancelled</option>
        </select>
        <button class="filter-button" type="submit">Filter</button>
        <button class="pagination-prev-button" @click="prevPage" :disabled="currentPage === 1">
          Previous
        </button>
        <p>Page {{ currentPage }} of {{ totalPages }}</p>
        <button
          class="pagination-next-button"
          @click="nextPage"
          :disabled="currentPage === totalPages"
        >
          Next
        </button>
      </form>

      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

      <div v-if="orders.length && !errorMessage" class="orders-list">
        <ul>
          <li v-for="order in orders" :key="order.id" class="order-card">
            <h2>Order ID: {{ order.id }}</h2>
            <p>Status: {{ order.status }}</p>
            <p>Order Date: {{ new Date(order.order_date).toLocaleString() }}</p>
            <ul class="product-list">
              <li v-for="product in order.products" :key="product.product_id">
                Product ID: {{ product.product_id }}, Quantity: {{ product.quantity }}
              </li>
            </ul>
          </li>
        </ul>
        <div class="pagination"></div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default defineComponent({
  data() {
    return {
      orders: [] as Array<{
        id: number
        status: string
        order_date: string
        products: Array<{ product_id: number; quantity: number }>
      }>,
      currentPage: 1,
      totalPages: 0,
      errorMessage: '',
      selectedStatus: ''
    }
  },
  setup() {
    const router = useRouter()

    const goHome = () => {
      router.push('/')
    }

    return { goHome }
  },
  methods: {
    getCookie(name: string): string | null {
      const value = `; ${document.cookie}`
      const parts = value.split(`; ${name}=`)
      if (parts.length === 2) return parts.pop()!.split(';').shift() || null
      return null
    },
    setCookie(name: string, value: string, days: number) {
      const date = new Date()
      date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000)
      const expires = `expires=${date.toUTCString()}`
      document.cookie = `${name}=${value};${expires};path=/`
    },
    async fetchOrders() {
      let token = this.getCookie('access_token')
      if (!token) {
        this.errorMessage = 'Authorization token is missing'
        await this.refreshToken()
        token = this.getCookie('access_token')
        if (!token) {
          this.errorMessage = 'Authorization failed. Please log in again.'
          return
        }
      }
      try {
        const params: any = {
          limit: 10,
          offset: (this.currentPage - 1) * 10
        }

        if (this.selectedStatus) {
          params.status = this.selectedStatus
        }

        const response = await axios.get('http://127.0.0.1:8000/api/orders/my-orders', {
          params,
          headers: {
            Authorization: `${token}`
          }
        })
        this.orders = response.data.orders
        this.totalPages = response.data.total_pages
      } catch (error: any) {
        this.errorMessage = 'Failed to fetch orders'
      }
    },
    async refreshToken() {
      const refreshToken = this.getCookie('refresh_token')
      if (!refreshToken) {
        this.errorMessage = 'Refresh token is missing'
        return
      }

      try {
        const response = await axios.post(
          `http://127.0.0.1:8000/api/auth/refresh`,
          {},
          {
            params: {
              refresh_token: refreshToken
            },
            headers: {
              accept: 'application/json'
            }
          }
        )

        const newAccessToken = response.data.access_token
        const newRefreshToken = response.data.refresh_token

        this.setCookie('access_token', newAccessToken, 1 / (24 * 60))
        this.setCookie('refresh_token', newRefreshToken, 7)
      } catch (error: any) {
        this.errorMessage = 'Failed to refresh tokens. Please log in again.'
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
        this.fetchOrders()
      }
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.fetchOrders()
      }
    }
  },

  mounted() {
    this.fetchOrders()
  }
})
</script>

<style scoped>
.profile-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #e9ecef;
}

.profile-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #f8f9fa;
  width: 80%;
  max-width: 800px;
  border-radius: 25px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.home-button {
  position: absolute;
  top: 20px;
  left: 20px;
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  background-color: #dfe7ec;
  color: #333;
  cursor: pointer;
}

.home-button:hover {
  background-color: #c4d4de;
}

.filter-form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.rounded-input,
.filter-button {
  padding: 8px;
  border-radius: 10px;
  border: 1px solid #ced4da;
}

.filter-button {
  background-color: #dfe7ec;
  cursor: pointer;
  border: none;
}

.filter-button:hover {
  background-color: #c4d4de;
}

.orders-list {
  width: 100%;
}

.order-card {
  background-color: #ffffff;
  padding: 20px;
  margin: 10px 0;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.product-list {
  padding-left: 20px;
}

.pagination {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-top: 20px;
}

.pagination-next-button {
  padding: 8px 16px;
  border-radius: 8px;
  background-color: #dfe7ec;
  border: none;
  cursor: pointer;
}

.pagination-next-button:disabled {
  background-color: #eaeaea;
  cursor: not-allowed;
}

.pagination-prev-button {
  padding: 8px 16px;
  border-radius: 8px;
  background-color: #dfe7ec;
  border: none;
  cursor: pointer;
}

.pagination-prev-button:disabled {
  background-color: #eaeaea;
  cursor: not-allowed;
}

.error-message {
  color: red;
  margin-top: 20px;
}
</style>
