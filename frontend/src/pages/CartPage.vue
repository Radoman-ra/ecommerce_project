<template>
  <div class="cart-wrapper">
    <div class="cart-container">
      <div class="top-bar">
        <button class="design-button" @click="goHome">Home</button>
        <div class="checkout-summary" v-if="cartItems.length > 0">
          <h3>Total Price: {{ totalPrice.toFixed(2) }}$</h3>
          <button class="design-button" @click="checkout">Checkout</button>
        </div>
      </div>
      <h1>Your Cart</h1>
      <div v-if="cartItems.length === 0">Your cart is empty.</div>
      <ul v-else class="cart-list">
        <li v-for="item in cartItems" :key="item.id" class="cart-item">
          <img
            :src="`http://127.0.0.1:8000/image/${item.name}.png`"
            alt="Product Image"
            class="cart-image"
          />
          <div class="cart-details">
            <div>{{ item.name }} - {{ item.price }}$</div>
            <div class="quantity-controls">
              <button class="quantity-button" @click="decreaseQuantity(item)">-</button>
              <input
                type="number"
                v-model.number="item.quantity"
                min="1"
                :max="item.availableQuantity"
                class="quantity-input"
                @input="handleInput(item)"
              />
              <button class="quantity-button" @click="increaseQuantity(item)">+</button>
              = {{ (item.price * item.quantity).toFixed(2) }}$
              <span v-if="item.availableQuantity < 999"
                >(Available: {{ item.availableQuantity }})</span
              >
            </div>
            <button class="remove-button" @click="removeFromCart(item.id)">Remove</button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default defineComponent({
  setup() {
    const router = useRouter()
    const cartItems = ref(JSON.parse(localStorage.getItem('cart') || '[]'))
    const timeoutIds = ref<number[]>([])

    const totalPrice = computed(() => {
      return cartItems.value.reduce(
        (acc: number, item: { price: number; quantity: number }) =>
          acc + item.price * item.quantity,
        0
      )
    })

    const removeFromCart = (id: number) => {
      const updatedCart = cartItems.value.filter((item: { id: number }) => item.id !== id)
      localStorage.setItem('cart', JSON.stringify(updatedCart))
      cartItems.value = updatedCart
    }

    const increaseQuantity = (item: {
      id: number
      quantity: number
      availableQuantity: number
    }) => {
      if (item.quantity < item.availableQuantity) {
        item.quantity++
        updateLocalStorage()
      }
    }

    const decreaseQuantity = (item: { id: number; quantity: number }) => {
      if (item.quantity > 1) {
        item.quantity--
        updateLocalStorage()
      } else {
        removeFromCart(item.id)
      }
    }

    const updateLocalStorage = () => {
      localStorage.setItem('cart', JSON.stringify(cartItems.value))
    }

    const handleInput = (item: { id: number; quantity: number; availableQuantity: number }) => {
      // Clear any existing timeout
      timeoutIds.value.forEach((id) => clearTimeout(id))
      timeoutIds.value = []

      // Set a new timeout to apply the value
      const timeoutId = setTimeout(() => {
        if (item.quantity < 1) {
          item.quantity = 1 // Set to minimum quantity of 1
        } else if (item.quantity > item.availableQuantity) {
          item.quantity = item.availableQuantity // Limit to max available quantity
        }
        updateLocalStorage()
      }, 500) // Delay of 500ms

      timeoutIds.value.push(timeoutId) // Store timeout ID
    }

    const checkout = async () => {
      const products = cartItems.value.map((item: { id: number; quantity: number }) => ({
        product_id: item.id,
        quantity: item.quantity
      }))

      const order = {
        products
      }

      console.log('Order payload:', order) // Debug: Log the order object

      const getAccessToken = () => {
        const cookieString = document.cookie
        const cookies = cookieString.split('; ')
        const tokenCookie = cookies.find((cookie) => cookie.startsWith('access_token='))
        return tokenCookie ? tokenCookie.split('=')[1] : null
      }

      const token = getAccessToken()
      console.log('JWT token:', token) // Debug: Log the JWT token

      try {
        const response = await fetch('http://127.0.0.1:8000/api/orders/', {
          method: 'POST',
          headers: {
            Authorization: `${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(order)
        })

        console.log('Response status:', response.status) // Debug: Log the response status
        console.log('Response headers:', response.headers) // Debug: Log the response headers

        const responseData = await response.json().catch(() => null)
        console.log('Response body:', responseData) // Debug: Log the response body

        if (response.status === 401) {
          alert('First you need to log in to your account')
          router.push('/login')
          return
        }

        if (!response.ok) {
          throw new Error('Network response was not ok')
        }

        alert('Order placed successfully!')
        localStorage.removeItem('cart')
        cartItems.value = []
      } catch (error) {
        console.error('Error placing order:', error)
        alert('Failed to place order. Please try again.')
      }
    }

    const goHome = () => {
      router.push('/')
    }

    // Fetch available quantities for products in the cart
    const fetchAvailableQuantities = async () => {
      try {
        const productIds = cartItems.value.map((item: { id: number }) => item.id).join(',')
        const response = await axios.get(
          `http://127.0.0.1:8000/api/products/available-quantities?ids=${productIds}`
        )

        // Assuming the response contains an array of objects like [{id: 1, available_quantity: 10}, ...]
        response.data.forEach((product: { id: number; quantity: number }) => {
          const cartItem = cartItems.value.find((item: { id: number }) => item.id === product.id)
          if (cartItem) {
            cartItem.availableQuantity = product.quantity
          }
        })
      } catch (error) {
        console.error('Error fetching available quantities:', error)
      }
    }

    // Fetch available quantities when the component is mounted
    fetchAvailableQuantities()

    return {
      cartItems,
      totalPrice,
      removeFromCart,
      increaseQuantity,
      decreaseQuantity,
      handleInput,
      checkout,
      goHome
    }
  }
})
</script>

<style scoped>
.cart-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #e9ecef;
}

.cart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #f8f9fa;
  width: 80%;
  max-width: 800px;
  border-radius: 25px; /* Закругленные углы */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Тень для эффекта объема */
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 15px; /* Закругленные углы внутри контейнера */
}

.cart-list {
  width: 100%;
  margin-top: 20px;
}

.cart-item {
  display: flex; /* Use flex for layout */
  align-items: center; /* Align items vertically */
  background-color: #ffffff;
  padding: 15px;
  margin: 10px 0;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.cart-image {
  width: 80px; /* Increased width for the product image */
  height: 80px; /* Increased height for the product image */
  border-radius: 5px; /* Optional: rounded corners */
  margin-right: 15px; /* Space between image and text */
}

.cart-details {
  flex-grow: 1; /* Allow details to take up remaining space */
}

.quantity-controls {
  display: flex; /* Use flex for layout */
  align-items: center; /* Align items vertically */
}

.quantity-button {
  padding: 6px 12px;
  background-color: #dfe7ec;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin: 0 5px; /* Space between buttons */
}

.quantity-button:hover {
  background-color: #cfd7e3;
}

.quantity-input {
  width: 50px; /* Fixed width for input */
  text-align: center; /* Center the text in the input */
}

.remove-button {
  padding: 6px 12px;
  background-color: #ffcccc;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}

.remove-button:hover {
  background-color: #ffb3b3;
}

.design-button {
  padding: 8px 16px;
  border-radius: 8px;
  background-color: #dfe7ec;
  border: none;
  cursor: pointer;
}

.design-button:disabled {
  background-color: #eaeaea;
  cursor: not-allowed;
}

.checkout-summary {
  display: flex;
  align-items: center;
  gap: 20px;
}
</style>
