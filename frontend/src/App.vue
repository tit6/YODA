<script setup lang="ts">
import { ref, onMounted } from 'vue'

const data = ref<any>(null)
const dataDb = ref<any>(null)
const error = ref<string | null>(null)
const errorDb = ref<string | null>(null)

const loadData = async (): Promise<void> => {
  try {
    const res = await fetch('/api/coucou', {
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

const testDb = async (): Promise<void> => {
  try {
    const db = await fetch('/api/db-test', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })

    console.log(db)

    if (!db.ok) throw new Error('Erreur serveur')

    dataDb.value = await db.json()
  } catch (err: unknown) {
    errorDb.value = err instanceof Error ? err.message : String(err)
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <h1>You did it!</h1>
  
  <button @click="testDb">
    test db
  </button>

  <div v-if="data">
    <h2>Réponse du back :</h2>
    <pre>{{ data }}</pre>
  </div>

  <p v-if="error" style="color: red;">
    Erreur : {{ error }}
  </p>

    <div v-if="data">
    <h2>Réponse du db :</h2>
    <pre>{{ dataDb }}</pre>
  </div>

  <p v-if="error" style="color: red;">
    Erreur : {{ errorDb }}
  </p>
</template>

<style scoped></style>
