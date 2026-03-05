/**
 * Mock API Service for development
 * Simulates backend API responses without a real server
 * Remove before production deployment
 *
 * IMPORTANT: All content, names, notes, and comments MUST be in English.
 * This is a strict requirement for consistency and maintainability.
 */

import {
  mockAuthResponse,
  mockAccounts,
  mockCategories,
  mockTransactions,
  mockBudgets,
  mockToken,
} from './mock-data';
import type {
  Account,
  Category,
  Transaction,
  Budget,
  AuthResponse,
  Summary,
  ChartData,
} from './mock-data';

// Custom error type for API errors
interface ApiError extends Error {
  response?: {
    data?: {
      message?: string;
    };
  };
}

// Simulate network delay
const delay = async (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Safe id generator to handle empty arrays
const getNextId = (arr: Array<{ id: number }>): number => {
  return arr.length === 0 ? 1 : Math.max(...arr.map((item) => item.id)) + 1;
};

const createApiError = (message: string): ApiError => {
  const error: ApiError = new Error(message);
  error.response = { data: { message } };
  return error;
};

/**
 * Authentication API
 */
export const mockAuthAPI = {
  async login(username: string, password: string): Promise<AuthResponse> {
    await delay(800);
    const isValidUsername = username === 'tomori';
    const isValidEmail = username === 'tomori@mygo.bandream';
    if ((isValidUsername || isValidEmail) && password === 'MyGO!!!!!No.1') {
      return mockAuthResponse;
    }
    throw createApiError('Invalid credentials');
  },

  async register(username: string, email: string, password: string): Promise<AuthResponse> {
    await delay(1000);
    if (!username || !email || !password) {
      throw createApiError('Missing required fields');
    }
    if (username === 'tomori') {
      throw createApiError('Username already exists');
    }
    return {
      token: mockToken,
      user: {
        id: 2,
        username,
        email,
        registrationDate: new Date().toISOString(),
      },
    };
  },

  async logout(): Promise<{ message: string }> {
    await delay(300);
    return { message: 'Logged out successfully' };
  },
};

/**
 * Accounts API
 */
export const mockAccountsAPI = {
  async getAccounts(): Promise<Account[]> {
    await delay(600);
    return mockAccounts;
  },

  async getAccount(id: number): Promise<Account> {
    await delay(400);
    const account = mockAccounts.find((a) => a.id === id);
    if (!account) {
      throw createApiError('Account not found');
    }
    return account;
  },

  async createAccount(data: Omit<Account, 'id' | 'userId' | 'balance'>): Promise<Account> {
    await delay(500);
    const newAccount: Account = {
      id: getNextId(mockAccounts),
      userId: 1,
      ...data,
      balance: 0,
    };
    mockAccounts.push(newAccount);
    return newAccount;
  },

  async updateAccount(id: number, data: Partial<Account>): Promise<Account> {
    await delay(500);
    const account = mockAccounts.find((a) => a.id === id);
    if (!account) {
      throw createApiError('Account not found');
    }
    Object.assign(account, data);
    return account;
  },

  async deleteAccount(id: number): Promise<{ message: string }> {
    await delay(400);
    const index = mockAccounts.findIndex((a) => a.id === id);
    if (index === -1) {
      throw createApiError('Account not found');
    }
    mockAccounts.splice(index, 1);
    return { message: 'Account deleted' };
  },
};

/**
 * Categories API
 */
export const mockCategoriesAPI = {
  async getCategories(): Promise<Category[]> {
    await delay(600);
    return mockCategories;
  },

  async getCategoryById(id: number): Promise<Category> {
    await delay(400);
    const category = mockCategories.find((c) => c.id === id);
    if (!category) {
      throw createApiError('Category not found');
    }
    return category;
  },

  async createCategory(data: Omit<Category, 'id' | 'userId'>): Promise<Category> {
    await delay(500);
    const newCategory: Category = {
      id: getNextId(mockCategories),
      userId: 1,
      ...data,
    };
    mockCategories.push(newCategory);
    return newCategory;
  },

  async updateCategory(id: number, data: Partial<Category>): Promise<Category> {
    await delay(500);
    const category = mockCategories.find((c) => c.id === id);
    if (!category) {
      throw createApiError('Category not found');
    }
    Object.assign(category, data);
    return category;
  },

  async deleteCategory(id: number): Promise<{ message: string }> {
    await delay(400);
    const index = mockCategories.findIndex((c) => c.id === id);
    if (index === -1) {
      throw createApiError('Category not found');
    }
    mockCategories.splice(index, 1);
    return { message: 'Category deleted' };
  },
};

/**
 * Transactions API
 */
export const mockTransactionsAPI = {
  async getTransactions(filters?: {
    accountId?: number;
    startDate?: string;
    endDate?: string;
  }): Promise<Transaction[]> {
    await delay(600);
    let results = [...mockTransactions];

    if (filters?.accountId) {
      results = results.filter((t) => t.accountId === filters.accountId);
    }

    if (filters?.startDate) {
      const startDate = filters.startDate;
      results = results.filter((t) => new Date(t.transactionDate) >= new Date(startDate));
    }

    if (filters?.endDate) {
      const endDate = filters.endDate;
      results = results.filter((t) => new Date(t.transactionDate) <= new Date(endDate));
    }

    return results;
  },

  async getTransaction(id: number): Promise<Transaction> {
    await delay(400);
    const transaction = mockTransactions.find((t) => t.id === id);
    if (!transaction) {
      throw createApiError('Transaction not found');
    }
    return transaction;
  },

  async createTransaction(
    data: Omit<Transaction, 'id' | 'userId' | 'crtTime' | 'uptTime'>,
  ): Promise<Transaction> {
    await delay(500);
    const now = new Date().toISOString();
    const newTransaction: Transaction = {
      id: getNextId(mockTransactions),
      userId: 1,
      ...data,
      crtTime: now,
      uptTime: now,
    };
    mockTransactions.push(newTransaction);
    return newTransaction;
  },

  async updateTransaction(id: number, data: Partial<Transaction>): Promise<Transaction> {
    await delay(500);
    const transaction = mockTransactions.find((t) => t.id === id);
    if (!transaction) {
      throw createApiError('Transaction not found');
    }
    const updated = {
      ...transaction,
      ...data,
      uptTime: new Date().toISOString(),
    };
    Object.assign(transaction, updated);
    return transaction;
  },

  async deleteTransaction(id: number): Promise<{ message: string }> {
    await delay(400);
    const index = mockTransactions.findIndex((t) => t.id === id);
    if (index === -1) {
      throw createApiError('Transaction not found');
    }
    mockTransactions.splice(index, 1);
    return { message: 'Transaction deleted' };
  },
};

/**
 * Budgets API
 */
export const mockBudgetsAPI = {
  async getBudgets(month?: string): Promise<Budget[]> {
    await delay(600);
    if (month) {
      return mockBudgets.filter((b) => b.budgetMonth === month);
    }
    return mockBudgets;
  },

  async getBudget(id: number): Promise<Budget> {
    await delay(400);
    const budget = mockBudgets.find((b) => b.id === id);
    if (!budget) {
      throw createApiError('Budget not found');
    }
    return budget;
  },

  async createBudget(data: Omit<Budget, 'id' | 'userId' | 'updatedAt'>): Promise<Budget> {
    await delay(500);
    const newBudget: Budget = {
      id: getNextId(mockBudgets),
      userId: 1,
      ...data,
      updatedAt: new Date().toISOString(),
    };
    mockBudgets.push(newBudget);
    return newBudget;
  },

  async updateBudget(id: number, data: Partial<Budget>): Promise<Budget> {
    await delay(500);
    const budget = mockBudgets.find((b) => b.id === id);
    if (!budget) {
      throw createApiError('Budget not found');
    }
    const updated = {
      ...budget,
      ...data,
      updatedAt: new Date().toISOString(),
    };
    Object.assign(budget, updated);
    return budget;
  },

  async deleteBudget(id: number): Promise<{ message: string }> {
    await delay(400);
    const index = mockBudgets.findIndex((b) => b.id === id);
    if (index === -1) {
      throw createApiError('Budget not found');
    }
    mockBudgets.splice(index, 1);
    return { message: 'Budget deleted' };
  },
};

/**
 * Dashboard API
 */
export const mockDashboardAPI = {
  async getSummary(): Promise<Summary> {
    await delay(600);

    // Derive the target month from the most recent transaction so the mock
    // summary stays accurate regardless of the current calendar date.
    const latestTransaction = mockTransactions.reduce<(typeof mockTransactions)[0] | null>(
      (latest, current) =>
        !latest || current.transactionDate > latest.transactionDate ? current : latest,
      null,
    );
    const targetMonth =
      latestTransaction?.transactionDate.slice(0, 7) ?? new Date().toISOString().slice(0, 7);

    const totalBalance = mockAccounts.reduce((sum, acc) => sum + acc.balance, 0);

    const monthlyTransactions = mockTransactions.filter((t) => {
      const transactionMonth = t.transactionDate.slice(0, 7);
      return transactionMonth === targetMonth;
    });

    const monthlyIncome = monthlyTransactions
      .filter((t) => {
        const category = mockCategories.find((c) => c.id === t.categoryId);
        return category?.type === 'income';
      })
      .reduce((sum, t) => sum + t.amount, 0);

    const monthlyExpense = monthlyTransactions
      .filter((t) => {
        const category = mockCategories.find((c) => c.id === t.categoryId);
        return category?.type === 'expense';
      })
      .reduce((sum, t) => sum + t.amount, 0);

    const savingsRate =
      monthlyIncome > 0 ? Math.round(((monthlyIncome - monthlyExpense) / monthlyIncome) * 100) : 0;

    return {
      totalBalance,
      monthlyIncome,
      monthlyExpense,
      savingsRate,
    };
  },

  async getChartData(): Promise<ChartData> {
    await delay(800);
    const last30Days = Array.from({ length: 30 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (29 - i));
      return date.toISOString().slice(0, 10);
    });

    const data = last30Days.map((date) => {
      const dayTransactions = mockTransactions.filter((t) => t.transactionDate.startsWith(date));
      const income = dayTransactions
        .filter((t) => {
          const category = mockCategories.find((c) => c.id === t.categoryId);
          return category?.type === 'income';
        })
        .reduce((sum, t) => sum + t.amount, 0);

      const expense = dayTransactions
        .filter((t) => {
          const category = mockCategories.find((c) => c.id === t.categoryId);
          return category?.type === 'expense';
        })
        .reduce((sum, t) => sum + t.amount, 0);

      return { date, income, expense };
    });

    return { data };
  },
};

/**
 * Central Mock API service
 * Use this to switch between real API and mock in development
 */
export const mockAPI = {
  auth: mockAuthAPI,
  accounts: mockAccountsAPI,
  categories: mockCategoriesAPI,
  transactions: mockTransactionsAPI,
  budgets: mockBudgetsAPI,
  dashboard: mockDashboardAPI,
};

export default mockAPI;
