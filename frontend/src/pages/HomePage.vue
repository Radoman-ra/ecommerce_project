<template>
  <div class="home-page">
    <AuthButtons />
    <SearchProducts />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import AuthButtons from '../components/HomeButtons.vue'
import SearchProducts from '../components/SearchProducts.vue'

export default defineComponent({
  components: {
    AuthButtons,
    SearchProducts
  }
})
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>
