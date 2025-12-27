
<template>
  <router-view />
</template>

<style>
@import './views/assets/variable.css';
@import './views/assets/component.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  background-color: var(--bg-page);
  color: var(--text-primary);
}

</style>
