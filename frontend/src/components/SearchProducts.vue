<template>
  <div class="search-products-container">
    <form @submit.prevent="searchProducts" class="search-form">
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
      <button type="submit" class="btn">Search</button>

      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

      <div v-if="products.length && !errorMessage">
        <h2>Search Results:</h2>
        <ul>
          <li v-for="product in products" :key="product.id" class="products-layout">
            {{ product.name }} - {{ product.price }}$
            <span>(Available: {{ product.availableQuantity }})</span>
            <button @click="addToCart(product)" class="btn">Add to Cart</button>
            <span v-if="getCartQuantity(product.id) > 0"
              >(In Cart: {{ getCartQuantity(product.id) }})</span
            >
          </li>
        </ul>
        <div class="pagination-container">
          <p>
            Page
            <input
              v-model.number="pageInput"
              type="number"
              min="1"
              :max="totalPages"
              @keyup.enter="goToPage(pageInput)"
              placeholder="Go to page"
              class="page-input"
            />
            of {{ totalPages }}
          </p>
          <div class="pagination-buttons">
            <button @click="goToPage(1)" :disabled="currentPage === 1" class="btn">First</button>
            <button @click="prevPage" :disabled="currentPage === 1" class="btn">Previous</button>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="btn">
              Next
            </button>
            <button
              @click="goToPage(totalPages)"
              :disabled="currentPage === totalPages"
              class="btn"
            >
              Last
            </button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive } from 'vue'
import axios from 'axios'

export default defineComponent({
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
      totalProducts: 0,
      limit: 10,
      errorMessage: '',
      cart: reactive(JSON.parse(localStorage.getItem('cart') || '[]')),
      pageInput: 1
    }
  },
  methods: {
    async searchProducts() {
      this.errorMessage = ''
      const params: any = {
        limit: this.limit,
        offset: (this.currentPage - 1) * this.limit
      }

      if (this.productName) {
        params.product_name = this.productName
      }
      if (this.creationDateFrom) {
        params.creation_date_from = this.creationDateFrom
      }
      if (this.creationDateTo) {
        params.creation_date_to = this.creationDateTo
      }
      if (this.categoryName) {
        params.category_name = this.categoryName
      }
      if (this.supplierName) {
        params.supplier_name = this.supplierName
      }
      if (this.minPrice) {
        params.min_price = this.minPrice
      }
      if (this.maxPrice) {
        params.max_price = this.maxPrice
      }

      try {
        const response = await axios.get('http://127.0.0.1:8000/api/search/products', {
          params
        })
        // Make sure your API response includes available quantities
        this.products = response.data.products.map(
          (product: { id: number; name: string; price: number; quantity: number }) => ({
            ...product,
            availableQuantity: product.quantity // Adjust this based on your actual API response
          })
        )
        this.totalProducts = response.data.total_products
        this.totalPages = response.data.total_pages
        this.pageInput = this.currentPage
      } catch (error: any) {
        if (error.response && error.response.status === 404) {
          this.errorMessage = 'No products found matching the criteria'
        } else {
          this.errorMessage = 'An error occurred while fetching products'
        }
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
    async goToPage(page: number) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        await this.searchProducts()
      }
    },
    addToCart(product: { id: number; name: string; price: number; availableQuantity: number }) {
      const existingItem = this.cart.find((item: { id: number }) => item.id === product.id)

      // Check if the desired quantity exceeds available stock
      if (existingItem) {
        if (existingItem.quantity < product.availableQuantity) {
          existingItem.quantity++
        } else {
          alert(`Cannot add more than available quantity: ${product.availableQuantity}`)
        }
      } else {
        // Only add if there's stock available
        if (1 <= product.availableQuantity) {
          this.cart.push({ ...product, quantity: 1 })
        } else {
          alert(`Cannot add more than available quantity: ${product.availableQuantity}`)
        }
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
.products-layout {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #ddd;
}

.search-products-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  background-color: #fff;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  max-width: 800px;
}

.input-field {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 15px;
  width: 150px;
}

.btn {
  padding: 10px 20px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 20px;
  color: #333;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #d8e2dc;
}
</style>
