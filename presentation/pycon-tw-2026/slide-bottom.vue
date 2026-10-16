<script setup lang="ts">
import { useSlideContext } from '@slidev/client'
const { $page } = useSlideContext()
</script>

<template>
  <div v-if="$page > 2" class="absolute bottom-1 right-2 flex flex-col items-center">
    <img src="/img/qr-repo.svg" class="w-11 h-11 rounded" />
    <div class="mono " style="font-size:7px;color:var(--yo-dim)">Yellow Olive repo</div>
  </div>
</template>
