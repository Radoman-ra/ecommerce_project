<template>
  <div>
    <SearchProducts />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import SearchProducts from './SearchProducts.vue'

export default defineComponent({
  components: {
    SearchProducts
  }
})
</script>

<style scoped></style>
