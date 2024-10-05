<template>
  <div class="marketplace-container">
    <!-- Левая колонка с фильтрами и кнопками -->
    <div class="filters">
      <HomeButtons />
      <form @submit.prevent="searchProducts" class="search-form">
        <h2>Search Filters</h2>
        <input v-model="productName" placeholder="Product Name" class="input-field" />
        <input
          v-model="creationDateFrom"
          placeholder="Creation Date From"
          type="date"
          class="input-field"
        />
        <input
          v-model="creationDateTo"
          placeholder="Creation Date To"
          type="date"
          class="input-field"
        />
        <input v-model="categoryName" placeholder="Category Name" class="input-field" />
        <input v-model="supplierName" placeholder="Supplier Name" class="input-field" />
        <input v-model="minPrice" placeholder="Min Price" type="number" class="input-field" />
        <input v-model="maxPrice" placeholder="Max Price" type="number" class="input-field" />
        <label for="limit" class="limit-label">Items per page:</label>
        <select v-model.number="limit" id="limit" class="input-field">
          <option :value="5">5</option>
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="30">30</option>
          <option :value="50">50</option>
        </select>
        <button type="submit" class="btn search-btn">Search</button>

        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      </form>
    </div>

    <!-- Правая колонка с результатами поиска продуктов -->
    <div class="products">
      <div v-if="products.length && !errorMessage">
        <div class="product-grid">
          <div v-for="product in products" :key="product.id" class="product-card">
            <h3>{{ product.name }}</h3>
            <p>${{ product.price }}</p>
            <p>Available: {{ product.availableQuantity }}</p>
            <button @click="addToCart(product)" class="btn add-cart-btn">Add to Cart</button>
            <p v-if="getCartQuantity(product.id) > 0">In Cart: {{ getCartQuantity(product.id) }}</p>
          </div>
        </div>

        <div class="pagination">
          <button @click="prevPage" :disabled="currentPage === 1" class="btn">Previous</button>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="btn">Next</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive } from 'vue'
import axios from 'axios'
import HomeButtons from './HomeButtons.vue'

export default defineComponent({
  components: {
    HomeButtons
  },
  data() {
    return {
      productName: '',
      creationDateFrom: '',
      creationDateTo: '',
      categoryName: '',
      supplierName: '',
      minPrice: '',
      maxPrice: '',
      products: [] as Array<{ id: number; name: string; price: number; availableQuantity: number }>,
      currentPage: 1,
      totalPages: 0,
      limit: 10,
      errorMessage: '',
      cart: reactive(JSON.parse(localStorage.getItem('cart') || '[]'))
    }
  },
  methods: {
    async searchProducts() {
      this.errorMessage = ''
      const params: any = {
        limit: this.limit,
        offset: (this.currentPage - 1) * this.limit
      }

      if (this.productName) params.product_name = this.productName
      if (this.creationDateFrom) params.creation_date_from = this.creationDateFrom
      if (this.creationDateTo) params.creation_date_to = this.creationDateTo
      if (this.categoryName) params.category_name = this.categoryName
      if (this.supplierName) params.supplier_name = this.supplierName
      if (this.minPrice) params.min_price = this.minPrice
      if (this.maxPrice) params.max_price = this.maxPrice

      try {
        const response = await axios.get('http://127.0.0.1:8000/api/search/products', { params })
        this.products = response.data.products.map(
          (product: { id: number; name: string; price: number; quantity: number }) => ({
            ...product,
            availableQuantity: product.quantity
          })
        )
        this.totalPages = response.data.total_pages
      } catch (error: any) {
        this.errorMessage = 'An error occurred while fetching products'
        console.error('Error fetching products:', error)
      }
    },
    async nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
        await this.searchProducts()
      }
    },
    async prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        await this.searchProducts()
      }
    },
    addToCart(product: { id: number; name: string; price: number; availableQuantity: number }) {
      const existingItem = this.cart.find((item: { id: number }) => item.id === product.id)
      if (existingItem) {
        if (existingItem.quantity < product.availableQuantity) existingItem.quantity++
        else alert(`Cannot add more than available quantity: ${product.availableQuantity}`)
      } else {
        if (1 <= product.availableQuantity) this.cart.push({ ...product, quantity: 1 })
        else alert(`Cannot add more than available quantity: ${product.availableQuantity}`)
      }
      localStorage.setItem('cart', JSON.stringify(this.cart))
      this.cart = reactive(JSON.parse(localStorage.getItem('cart') || '[]'))
    },
    getCartQuantity(productId: number): number {
      const item = this.cart.find((item: { id: number }) => item.id === productId)
      return item ? item.quantity : 0
    }
  }
})
</script>

<style scoped>
.marketplace-container {
  display: flex;
  justify-content: center; /* Center the content horizontally */
  padding: 20px;
}

.filters {
  width: 20%;
  position: fixed; /* Keep it fixed on the left */
  top: 0;
  left: 0;
  height: 100vh;
  overflow-y: auto;
  background-color: #f9f9f9;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.products {
  margin-left: 20%; /* Leave space for the fixed filters */
  padding: 20px;
  height: calc(100vh - 40px);
  overflow-y: auto;
  display: flex;
  justify-content: center; /* Center the product grid */
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
}

.input-field {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.btn {
  padding: 10px;
  background-color: #007bff;
  border: none;
  border-radius: 5px;
  color: white;
  cursor: pointer;
}

.btn:hover {
  background-color: #0056b3;
}

.product-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  max-width: 800px; /* Set a maximum width for the grid */
  width: 100%; /* Full width for responsiveness */
}

.product-card {
  border: 1px solid #ccc;
  border-radius: 10px;
  padding: 15px;
  width: 200px; /* Fixed width for the product cards */
  background-color: white;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.pagination {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}
</style>
