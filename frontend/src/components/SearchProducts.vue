<template>
  <div class="marketplace-container">
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

    <div class="products">
      <div v-if="products.length && !errorMessage">
        <div class="product-grid">
          <div v-for="product in products" :key="product.id" class="product-card">
            <img
              :src="`http://127.0.0.1:8000/image/${product.name}.png`"
              alt="Product Image"
              class="product-image"
            />
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-price">${{ product.price }}</p>
            <p class="product-quantity">Available: {{ product.availableQuantity }}</p>
            <button @click="addToCart(product)" class="btn add-cart-btn">Add to Cart</button>
            <p v-if="getCartQuantity(product.id) > 0" class="cart-quantity">
              In Cart: {{ getCartQuantity(product.id) }}
            </p>
            <button @click="openModal(product)" class="btn details-btn">View Details</button>
          </div>
        </div>

        <div class="pagination">
          <button @click="prevPage" :disabled="currentPage === 1" class="btn">Previous</button>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="btn">Next</button>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <span @click="closeModal" class="close">&times;</span>
        <h2>{{ selectedProduct.name }}</h2>
        <img :src="selectedProduct.imageUrl" alt="Product Image" class="modal-product-image" />
        <p><strong>Description:</strong> {{ selectedProduct.description }}</p>
        <p><strong>Price:</strong> ${{ selectedProduct.price }}</p>
        <p><strong>Available Quantity:</strong> {{ selectedProduct.availableQuantity }}</p>
        <button @click="addToCart(selectedProduct)" class="btn add-cart-btn">Add to Cart</button>
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
      products: [] as Array<{
        id: number
        name: string
        price: number
        availableQuantity: number
        imageUrl: string
        description: string
      }>,
      currentPage: 1,
      totalPages: 0,
      limit: 10,
      errorMessage: '',
      showModal: false,
      selectedProduct: {} as {
        id: number
        name: string
        price: number
        availableQuantity: number
        description: string
        imageUrl: string
      },
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
          (product: {
            id: number
            name: string
            price: number
            quantity: number
            description: string
            photo_path: string
          }) => ({
            ...product,
            availableQuantity: product.quantity,
            imageUrl: `http://127.0.0.1:8000/image/${product.name}.png`,
            description: product.description
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
    },
    openModal(product: {
      id: number
      name: string
      price: number
      availableQuantity: number
      description: string
      photo_path: string
    }) {
      this.selectedProduct = {
        ...product,
        imageUrl: `http://127.0.0.1:8000/image/${product.name}.png`
      }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
      this.selectedProduct = {} as {
        id: number
        name: string
        price: number
        availableQuantity: number
        description: string
        imageUrl: string
      }
    }
  }
})
</script>

<style scoped>
body {
  font-family: 'Arial', sans-serif;
  background-color: #f4f7f9;
  color: #333;
}

.marketplace-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  position: relative;
}

.filters {
  width: 25%;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  padding: 20px;
  background-color: #ffffff;
  border-right: 2px solid #ddd;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.search-form {
  display: flex;
  flex-direction: column;
}

.input-field {
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ccc;
  border-radius: 5px;
  transition: border-color 0.3s;
}

.input-field:focus {
  border-color: #007bff;
}

.search-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background-color: #0056b3;
}

.limit-label {
  margin: 10px 0 5px;
}

.products {
  margin-left: 25%;
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  width: 100%;
}

.product-card {
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 10px;
  text-align: center;
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.product-card:hover {
  transform: scale(1.03);
}

.product-image {
  max-width: 100%;
  height: auto;
  border-radius: 5px;
}

.product-name {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 10px 0;
}

.product-price {
  font-size: 1rem;
  color: #28a745;
}

.product-quantity {
  font-size: 0.9rem;
  color: #555;
}

.cart-quantity {
  font-size: 0.8rem;
  color: #007bff;
}

.add-cart-btn,
.details-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 8px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-cart-btn:hover,
.details-btn:hover {
  background-color: #218838;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  position: relative;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.close {
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 20px;
  cursor: pointer;
  color: #333;
}

.modal-product-image {
  max-width: 100%;
  height: auto;
  border-radius: 5px;
}

.error-message {
  color: red;
  margin-top: 10px;
  font-size: 0.9rem;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.pagination .btn {
  margin: 0 10px;
}
</style>
