<template>
  <div class="container mt-3">
    <ExpenseForm />
  </div>
</template>

<script>
import ExpenseForm from './expenses/ExpenseForm.vue'; // Import the ExpenseForm component

export default {
  components: {
    ExpenseForm // Register the ExpenseForm component
  },
};
</script>
