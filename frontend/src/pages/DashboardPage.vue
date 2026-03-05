<script setup lang="ts">
import { ref, onMounted } from 'vue';
import SummaryCards from '@/components/SummaryCards.vue';
import RecentTransactionsList from '@/components/RecentTransactionsList.vue';
import { mockAPI } from '@/api/mock';
import type { Summary, Transaction, Category } from '@/api/mock-data';

defineOptions({ name: 'DashboardPage' });

const summaryData = ref<Summary | null>(null);
const recentTransactions = ref<Transaction[]>([]);
const categories = ref<Category[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

async function fetchDashboardData() {
  isLoading.value = true;
  error.value = null;

  try {
    // Parallel data fetching
    const [summary, transactions, categoriesData] = await Promise.all([
      mockAPI.dashboard.getSummary(),
      mockAPI.transactions.getTransactions(),
      mockAPI.categories.getCategories(),
    ]);

    summaryData.value = summary;
    recentTransactions.value = transactions;
    categories.value = categoriesData;
  } catch (err) {
    console.error('Failed to load dashboard data:', err);
    error.value = 'Unable to load dashboard. Please try again.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  void fetchDashboardData();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Error Message -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-sm text-red-800">{{ error }}</p>
    </div>

    <!-- Summary Cards -->
    <SummaryCards :data="summaryData" :is-loading="isLoading" />

    <!-- Recent Transactions -->
    <RecentTransactionsList
      :transactions="recentTransactions"
      :categories="categories"
      :is-loading="isLoading"
    />
  </div>
</template>
