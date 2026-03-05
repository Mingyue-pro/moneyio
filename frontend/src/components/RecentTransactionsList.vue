<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import type { Transaction, Category } from '@/api/mock-data';

defineOptions({ name: 'RecentTransactionsList' });

interface Props {
  transactions?: Transaction[];
  categories?: Category[];
  isLoading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  transactions: () => [],
  categories: () => [],
  isLoading: false,
});

const router = useRouter();

const recentTransactions = computed(() => {
  return [...props.transactions]
    .sort((a, b) => new Date(b.transactionDate).getTime() - new Date(a.transactionDate).getTime())
    .slice(0, 5);
});

const getCategoryName = (categoryId: number) => {
  return props.categories.find((c) => c.id === categoryId)?.name ?? 'Unknown';
};

const getCategoryType = (categoryId: number) => {
  return props.categories.find((c) => c.id === categoryId)?.type ?? 'expense';
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const formatAmount = (amount: number, type: string) => {
  const formatted = amount.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  });
  return type === 'income' ? `+${formatted}` : `-${formatted}`;
};

const getAmountColor = (type: string) => {
  return type === 'income' ? 'text-green-600' : 'text-red-600';
};

function goToTransactions() {
  void router.push('/transactions');
}
</script>

<template>
  <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
    <div class="px-6 py-4 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-900">Recent Transactions</h2>
    </div>

    <div class="divide-y divide-gray-200">
      <!-- Loading State -->
      <div v-if="isLoading" class="divide-y divide-gray-200">
        <div v-for="i in 5" :key="i" class="px-6 py-4 flex items-center justify-between">
          <div class="flex-1">
            <div class="h-4 bg-gray-200 rounded w-24 mb-2 animate-pulse"></div>
            <div class="h-3 bg-gray-200 rounded w-16 animate-pulse"></div>
          </div>
          <div class="h-6 bg-gray-200 rounded w-20 animate-pulse"></div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="recentTransactions.length === 0" class="px-6 py-12">
        <p class="text-center text-gray-500">No transactions yet. Start by adding one!</p>
      </div>

      <!-- Transactions List -->
      <div v-else>
        <div
          v-for="transaction in recentTransactions"
          :key="transaction.id"
          class="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">
              {{ getCategoryName(transaction.categoryId) }}
            </p>
            <p class="text-xs text-gray-500">{{ formatDate(transaction.transactionDate) }}</p>
          </div>
          <p
            :class="[
              'text-sm font-semibold ml-4',
              getAmountColor(getCategoryType(transaction.categoryId)),
            ]"
          >
            {{ formatAmount(transaction.amount, getCategoryType(transaction.categoryId)) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="px-6 py-4 bg-gray-50 border-t border-gray-200">
      <button
        type="button"
        class="w-full text-center text-sm font-medium text-blue-600 hover:text-blue-700 py-2 rounded-md hover:bg-blue-50 transition-colors"
        @click="goToTransactions"
      >
        View All Transactions
      </button>
    </div>
  </div>
</template>
