<script setup lang="ts">
import { ref, onMounted } from 'vue'

const data = ref<any>(null)
const error = ref<string | null>(null)

const loadData = async (): Promise<void> => {
  try {
    const res = await fetch('/coucou', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })

    console.log(res)

    if (!res.ok) throw new Error('Erreur serveur')

    data.value = await res.json()
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : String(err)
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <h1>You did it!</h1>
  
  <button @click="loadData">
    Charger les données du back
  </button>

  <div v-if="data">
    <h2>Réponse du back :</h2>
    <pre>{{ data }}</pre>
  </div>

  <p v-if="error" style="color: red;">
    Erreur : {{ error }}
  </p>
</template>

<style scoped></style>
