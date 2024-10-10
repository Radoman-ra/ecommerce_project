<template>
  <div class="profile-wrapper">
    <div class="header">
      <div class="auth-buttons">
        <HomeButtons />
      </div>
    </div>
    <div class="profile-container">
      <h1 v-if="orders.length > 0">My Orders</h1>
      <!-- Display the filter only if there are orders -->
      <form class="filter-form" v-if="orders.length > 0" @submit.prevent="fetchOrders">
        <div class="order-filter">
          <label for="status">Order Status:</label>
          <select v-model="selectedStatus" class="rounded-input">
            <option value="">All</option>
            <option value="Pending">Pending</option>
            <option value="Shipped">Shipped</option>
            <option value="Delivered">Delivered</option>
            <option value="Cancelled">Cancelled</option>
          </select>
          <button class="filter-button" type="submit">Filter</button>
        </div>
      </form>

      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

      <!-- If there are orders, show them; otherwise, show a no orders message -->
      <div v-if="orders.length && !errorMessage" class="orders-list">
        <ul>
          <li v-for="order in orders" :key="order.id" class="order-card">
            <div class="order-header">
              <h2 class="order-id">Order ID: {{ order.id }}</h2>
              <p>Order Date: {{ new Date(order.order_date).toLocaleString() }}</p>
              <p class="order-status">Status: {{ order.status }}</p>
            </div>

            <div class="progress-bar">
              <div class="progress-fill" :style="getProgressBarStyle(order.status)"></div>
              <span v-if="order.status === 'Cancelled'" class="cancelled-text">Cancelled</span>
            </div>

            <ul class="product-list">
              <li v-for="product in order.products" :key="product.product_id" class="product-card">
                <div v-if="product.details" class="product-info">
                  <img :src="product.details.imageUrl" alt="Product Image" class="product-image" />
                  <div class="product-details">
                    <div>
                      <div class="product-name">{{ product.details.name }}</div>
                      <div class="product-category">
                        Category: {{ product.details.category.name }}
                      </div>
                    </div>
                    <div class="product-price">
                      {{ product.details.price }} x {{ product.quantity }} =
                      {{ (product.details.price * product.quantity).toFixed(2) }}
                    </div>
                  </div>
                  <div class="product-supplier">
                    <div class="supplier-text">Supplier:</div>
                    <div class="product-supplier-info">
                      <div class="supplier-name">{{ product.details.supplier.name }}</div>
                      <div class="supplier-email">{{ product.details.supplier.contact_email }}</div>
                      <div class="supplier-phone">
                        Phone: {{ product.details.supplier.phone_number }}
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else>
                  <p>Loading product details...</p>
                </div>
              </li>
            </ul>

            <div class="final-price">Total Price: ${{ calculateOrderTotal(order).toFixed(2) }}</div>
          </li>
        </ul>
      </div>

      <!-- Display no orders message if the orders list is empty -->
      <div v-else class="error">
        <p>You have no orders yet.</p>
      </div>

      <!-- Pagination only if there are orders -->
      <div v-if="orders.length > 0" class="pagination">
        <button class="pagination-prev-button" @click="prevPage" :disabled="currentPage === 1">
          &#8592;
        </button>
        <p>Page {{ currentPage }} of {{ totalPages }}</p>
        <button
          class="pagination-next-button"
          @click="nextPage"
          :disabled="currentPage === totalPages"
        >
          &rarr;
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import HomeButtons from './HomeButtons.vue'

export default defineComponent({
  components: {
    HomeButtons
  },
  data() {
    return {
      orders: [] as Array<{
        id: number
        status: string
        order_date: string
        products: Array<{ product_id: number; quantity: number; details?: any }>
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
        const orders = response.data.orders
        this.orders = orders
        this.totalPages = response.data.total_pages

        for (const order of this.orders) {
          for (const product of order.products) {
            this.fetchProductDetails(product)
          }
        }
      } catch (error: any) {
        this.errorMessage = 'Failed to fetch orders'
      }
    },
    async fetchProductDetails(product: any) {
      try {
        const productResponse = await axios.get(
          `http://127.0.0.1:8000/api/products/${product.product_id}`
        )
        const productDetails = productResponse.data

        const categoryResponse = await axios.get(
          `http://127.0.0.1:8000/api/categories/${productDetails.category_id}`
        )
        const categoryDetails = categoryResponse.data

        const supplierResponse = await axios.get(
          `http://127.0.0.1:8000/api/suppliers/${productDetails.supplier_id}`
        )
        const supplierDetails = supplierResponse.data

        product.details = {
          ...productDetails,
          imageUrl: `http://127.0.0.1:8000/static/images/100x100/${productDetails.photo_path}`,
          category: categoryDetails,
          supplier: supplierDetails
        }
      } catch (error: any) {
        console.error('Failed to fetch product details', error)
      }
    },
    calculateOrderTotal(order: any) {
      return order.products.reduce((total: number, product: any) => {
        return total + product.details.price * product.quantity
      }, 0)
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
    getProgressBarStyle(status: string) {
      let width = '0%'
      let backgroundColor = '#00aaff'

      if (status === 'pending') {
        width = '33%'
      } else if (status === 'shipped') {
        width = '66%'
      } else if (status === 'delivered') {
        backgroundColor = 'green'
        width = '100%'
      } else if (status === 'cancelled') {
        backgroundColor = 'red'
        width = '100%'
      }

      return {
        width: width,
        backgroundColor: backgroundColor
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
.error {
  color: rgb(105, 105, 105);
  font-weight: bold;
  font-size: 1.2em;
  text-align: center;
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 350px;
}
.profile-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #e9ecef;
}
.product-image {
  max-width: 100px;
  border-radius: 12px;
}

.product-card {
  background-color: #f8f9fa;
  padding: 15px;
  margin: 10px 0;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #e9ecef;
  border-radius: 10px;
  margin: 10px 0;
  position: relative;
}

.product-info {
  display: flex;
  gap: 20px;
}
.progress-fill {
  height: 100%;
  border-radius: 10px;
}

.product-supplier {
  display: flex;
  margin-left: auto;
  gap: 20px;
}

.supplier-text {
  font-weight: bold;
  color: rgba(58, 58, 58, 0.315);
}

.product-supplier-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.final-price {
  margin-top: 10px;
  font-weight: 550;
  margin-right: auto;
}

.product-details {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-price {
  font-weight: 550;
  margin-top: auto;
}
.cancelled-text {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  font-weight: bold;
}

.profile-container {
  min-height: 350px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #f8f9fa;
  width: 80%;
  max-width: 800px;
  border-radius: 25px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.home-button {
  padding: 8px 16px;
  border-radius: 8px;
  background-color: #dfe7ec;
  border: none;
  cursor: pointer;
  position: absolute;
  top: 20px;
  left: 20px;
}

.home-button:hover {
  background-color: #cfd7e3;
}

.filter-form {
  display: flex;
  gap: 10px;
  width: 100%;
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
  background-color: #cfd7e3;
}

.orders-list {
  width: 100%;
}

.order-header {
  display: flex;
  width: 100%;
  margin-bottom: 10px;
}

.order-id {
  margin-right: auto;
}

.order-status {
  margin-left: auto;
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
  margin-left: auto;
  display: flex;
  gap: 10px;
  align-items: center;
}

.pagination-next-button,
.pagination-prev-button {
  padding: 8px 16px;
  border-radius: 8px;
  background-color: #dfe7ec;
  border: none;
  cursor: pointer;
}

.pagination-next-button:disabled,
.pagination-prev-button:disabled {
  background-color: #eaeaea;
  cursor: not-allowed;
}

.error-message {
  color: red;
  margin-top: 20px;
}

.header {
  margin-top: 6rem;
  max-width: 800px;
  width: 80%;
}
</style>
