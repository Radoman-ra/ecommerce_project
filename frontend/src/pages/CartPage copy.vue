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
          {{ item.name }} - {{ item.price }}$ x
          <input
            type="number"
            v-model.number="item.quantity"
            min="1"
            @input="updateQuantity(item)"
          />
          = {{ (item.price * item.quantity).toFixed(2) }}$
          <button class="remove-button" @click="removeFromCart(item.id)">Remove</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  setup() {
    const router = useRouter()
    const cartItems = ref(JSON.parse(localStorage.getItem('cart') || '[]'))

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

    const updateQuantity = (item: { id: number; quantity: number }) => {
      if (item.quantity < 1) {
        removeFromCart(item.id)
      } else {
        const updatedCart = cartItems.value.map((cartItem: { id: number; quantity: number }) =>
          cartItem.id === item.id ? { ...cartItem, quantity: item.quantity } : cartItem
        )
        localStorage.setItem('cart', JSON.stringify(updatedCart))
        cartItems.value = updatedCart
      }
    }

    const checkout = async () => {
      const products = cartItems.value.map((item: { id: number; quantity: number }) => ({
        product_id: item.id,
        quantity: item.quantity
      }))

      const order = {
        products,
        status: 'pending' // Add the status field here
      }

      const getAccessToken = () => {
        const cookieString = document.cookie
        const cookies = cookieString.split('; ')
        const tokenCookie = cookies.find((cookie) => cookie.startsWith('access_token='))
        return tokenCookie ? tokenCookie.split('=')[1] : null
      }

      const token = getAccessToken()

      const curlCommand = `curl -X POST http://127.0.0.1:8000/api/orders/ \\
-H "Authorization: ${token}" \\
-H "Content-Type: application/json" \\
-d '${JSON.stringify(order, null, 2)}'`

      console.log('Curl command:', curlCommand)

      try {
        const response = await fetch('http://127.0.0.1:8000/api/orders/', {
          method: 'POST',
          headers: {
            Authorization: `${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(order)
        })

        if (response.status === 401) {
          alert('First you need to log in to your account')
          router.push('/login')
          return
        }

        if (!response.ok) {
          throw new Error('Network response was not ok')
        }

        const responseData = await response.json()
        alert('Order placed successfully!')
        console.log('Server response:', responseData)
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

    return {
      cartItems,
      totalPrice,
      removeFromCart,
      updateQuantity,
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
  background-color: #ffffff;
  padding: 15px;
  margin: 10px 0;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
