<template>
  <div>
    <div class="header">
      <div class="auth-buttons">
        <HomeButtons />
      </div>
    </div>
    <div class="marketplace-container">
      <div class="filters">
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
        <div v-if="products.length && !errorMessage" class="product-grid">
          <div
            v-for="product in products"
            :key="product.id"
            @click="openModal(product)"
            class="product-card"
          >
            <div class="image-container">
              <img
                :src="`http://127.0.0.1:8000/image/${product.name}.png`"
                alt="Product Image"
                class="product-image"
              />
              <span v-if="getCartQuantity(product.id) > 0" class="cart-tag">In Cart</span>
              <span v-if="product.availableQuantity === 0" class="outofstock-tag"
                >Out of stock</span
              >
            </div>
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-price">${{ product.price }}</p>
            <div style="display: flex; gap: 8px; justify-content: center"></div>
          </div>
        </div>
        <div class="pagination">
          <div class="nav-btn-prev">
            <button @click="goToPage(1)" :disabled="currentPage === 1" class="pagination-btn first">
              First
            </button>
            <button @click="prevPage" :disabled="currentPage === 1" class="pagination-btn prev">
              &#8592;
            </button>
          </div>
          <div class="nav-page">
            <label class="pagination-label">{{ currentPage }} / {{ totalPages }}</label>
          </div>
          <div class="nav-btn-next">
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="pagination-btn next"
            >
              &rarr;
            </button>
            <button
              @click="goToPage(totalPages)"
              :disabled="currentPage === totalPages"
              class="pagination-btn last"
            >
              Last
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="showModal"
        class="modal"
        @click="closeModal"
        aria-modal="true"
        role="dialog"
        tabindex="-1"
      >
        <div class="modal-content" @click.stop>
          <span @click="closeModal" class="close" role="button" aria-label="Close modal"
            >&times;</span
          >
          <div class="modal-main">
            <img :src="selectedProduct.imageUrl" alt="Product Image" class="modal-product-image" />
            <div class="modal-info">
              <h2 class="modal-title">{{ selectedProduct.name }}</h2>
              <p class="modal-price">${{ selectedProduct.price }}</p>
              <p>
                <strong v-if="selectedProduct.availableQuantity > 0" class="modal-qty"
                  >In Stock: {{ selectedProduct.availableQuantity }}</strong
                >
                <strong v-else class="modal-outofstock">Out of Stock</strong>
              </p>
              <div class="modal-description">
                <label class="modal-description-label">Description:</label>
                <p>{{ selectedProduct.description }}</p>
              </div>
              <div class="cart-section">
                <button
                  v-if="!(selectedProduct.availableQuantity == 0)"
                  @click="addToCart(selectedProduct)"
                  class="btn add-cart-btn"
                >
                  Add to Cart
                </button>
              </div>
            </div>
          </div>
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
    async goToPage(page: number) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
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
  },
  mounted() {
    this.searchProducts()
  }
})
</script>

<style scoped>
body {
  font-family: 'Arial', sans-serif;
  background-color: #f4f7f9;
  color: #333;
}

.auth-buttons {
  margin: auto;
  display: flex;
  justify-content: flex-end;
  max-width: 80rem;
}
.header {
  margin-top: 6rem;
}
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.cart-section {
  display: flex;
}

.modal-description-label {
  font-weight: 550;
}

.modal-price {
  font-size: 1.5rem;
  margin-bottom: 10px;
  color: #616e70;
}
.modal-qty {
  margin-bottom: 10px;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 700px;
  width: 90%;
  position: relative;
}

.modal-main {
  display: flex;
}

.modal-title {
  font-weight: 600;
  font-size: 1.5rem;
}

.modal-outofstock {
  color: red;
}

.modal-product-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.close {
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 1.5rem;
  cursor: pointer;
  color: #555;
}

.close:hover {
  color: #f00;
}

.btn.add-cart-btn {
  background-color: #28a745;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%;
  margin-bottom: auto;
}

.modal-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px 10px 0px 10px;
}

.btn.add-cart-btn:hover {
  background-color: #218838;
}

.marketplace-container {
  border: 1px solid #ccc;
  border-radius: 20px;
  margin: auto;
  max-width: 80rem;
  height: 100%;
  display: flex;
  position: relative;
}

.filters {
  margin-top: 0.5%;
  height: auto;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border-right: 2px solid #ddd;
  overflow-y: auto;
  overflow-x: hidden;
  width: 30%;
}

.search-form {
  display: flex;
  flex-direction: column;
}

.input-field {
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn {
  padding: 10px;
  margin: 10px 0;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-btn {
  background-color: #1e90ff;
}

.pagination {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-bottom: 10px;
  max-width: 100%;
}

.pagination-btn {
  background-color: #007bff;
  border: none;
  color: white;
  padding: 8px 16px;
  margin: 0 5px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.pagination-btn:disabled {
  background-color: #c0c0c0;
  cursor: not-allowed;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.pagination-label {
  font-weight: bold;
  font-size: 16px;
  color: #333;
  min-width: 80px;
  text-align: center;
}

.nav-btn-prev,
.nav-btn-next {
  display: flex;
  align-items: center;
}

@media (max-width: 500px) {
  .pagination {
    flex-direction: column;
  }
  .pagination-btn {
    width: 100%;
    margin: 5px 0;
  }
  .pagination-label {
    margin: 10px 0;
  }
}

.error-message {
  color: red;
  font-weight: bold;
}

.nav-btn-prev,
.nav-btn-next {
  display: flex;
  align-items: center;
  flex-direction: row;
}

.products {
  width: 100%;
  padding: 1rem;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  width: 100%;
}

.product-card {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  max-width: 200px;
  margin: 0 auto;
  width: 100%;
}

.product-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
}

.image-container {
  position: relative;
  display: flex;
}

.cart-tag {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: rgb(239, 246, 255);
  color: rgba(37, 136, 223, 0.84);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  z-index: 10;
}

.outofstock-tag {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: rgb(255, 239, 239);
  color: rgba(223, 37, 37, 0.84);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  z-index: 10;
}

.product-name {
  margin-top: 20px;
  text-align: left;
  font-size: 1.2em;
  margin-bottom: 10px;
}

.product-price {
  font-weight: bold;
  margin-top: 15px;
  text-align: left;
  color: #000000;
  font-size: 1.1em;
  margin-bottom: 10px;
}

.product-quantity {
  margin-bottom: 15px;
}

.cart-quantity {
  margin-top: 10px;
  font-weight: bold;
  color: green;
}

.modal {
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.4);
}

.modal-content {
  background-color: #fefefe;
  margin: 10% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 40%;
  position: relative;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
}

.close:hover,
.close:focus {
  color: #000;
  text-decoration: none;
  cursor: pointer;
}

@media (max-width: 768px) {
  .products {
    width: 100%;
    padding-left: 0;
    margin-left: 0;
  }

  .product-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

@media (max-width: 480px) {
  .products {
    width: 100%;
    padding-left: 0;
    margin-left: 0;
  }

  .product-grid {
    grid-template-columns: 1fr;
  }

  .filters {
    width: 100%;
    position: relative;
    height: auto;
    border-right: none;
  }
}
</style>
