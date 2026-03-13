<script setup lang="ts">
import { reactive, ref, computed, onMounted, watch } from 'vue';
import {
  Dialog,
  DialogPanel,
  TransitionRoot,
  TransitionChild,
  Listbox,
  ListboxButton,
  ListboxOptions,
  ListboxOption,
} from '@headlessui/vue';
import { CheckIcon, ChevronDownIcon } from '@heroicons/vue/20/solid';
import { mockAPI } from '@/api/mock';
import type { Account } from '@/api/mock-data';

defineOptions({ name: 'AccountFormModal' });

const props = withDefaults(
  defineProps<{
    isOpen: boolean;
    mode: 'create' | 'edit';
    account?: Account | null;
  }>(),
  {
    account: null,
  },
);

const emit = defineEmits<{
  close: [];
  saved: [];
}>();

const form = reactive({
  name: '',
  type: 'checking' as 'savings' | 'checking' | 'credit',
  balance: '',
});

const errors = reactive({
  name: '',
  type: '',
  balance: '',
});

const submitError = ref<string>('');
const isSaving = ref(false);

const ACCOUNT_TYPES: Array<{ value: 'savings' | 'checking' | 'credit'; label: string }> = [
  { value: 'savings', label: 'Savings Account' },
  { value: 'checking', label: 'Checking Account' },
  { value: 'credit', label: 'Credit Card' },
];

const hasErrors = computed(() => !!errors.name || !!errors.type || !!errors.balance);

const selectedTypeLabel = computed(() => {
  const type = ACCOUNT_TYPES.find((t) => t.value === form.type);
  return type?.label ?? 'Select type';
});

const isEditMode = computed(() => props.mode === 'edit');

function validate(): boolean {
  errors.name = form.name.trim() ? '' : 'Account name is required';
  errors.type = form.type ? '' : 'Account type is required';

  if (form.balance === '') {
    errors.balance = '';
  } else if (isNaN(Number(form.balance))) {
    errors.balance = 'Please enter a valid balance';
  } else {
    errors.balance = '';
  }

  return !hasErrors.value;
}

function resetForm(): void {
  form.name = '';
  form.type = 'checking';
  form.balance = '';
  errors.name = '';
  errors.type = '';
  errors.balance = '';
  submitError.value = '';
}

function initializeForm(): void {
  if (isEditMode.value && props.account) {
    form.name = props.account.name;
    form.type = props.account.type;
    form.balance = props.account.balance.toString();
  } else {
    resetForm();
  }
}

async function submitForm(): Promise<void> {
  if (!validate()) return;

  isSaving.value = true;
  submitError.value = '';
  try {
    if (isEditMode.value && props.account) {
      await mockAPI.accounts.updateAccount(props.account.id, {
        name: form.name.trim(),
        type: form.type,
        balance: form.balance === '' ? 0 : Number(form.balance),
      });
    } else {
      const payload: Omit<Account, 'id' | 'userId' | 'balance'> & { balance?: number } = {
        name: form.name.trim(),
        type: form.type,
      };

      if (form.balance !== '') {
        payload.balance = Number(form.balance);
      }

      await mockAPI.accounts.createAccount(payload);
    }
    emit('saved');
    handleClose();
  } catch (err) {
    console.error('Failed to save account', err);
    submitError.value = 'Failed to save account. Please try again.';
  } finally {
    isSaving.value = false;
  }
}

function handleClose(): void {
  resetForm();
  emit('close');
}

onMounted(() => {
  initializeForm();
});

watch(
  () => [props.isOpen, props.mode, props.account],
  () => {
    initializeForm();
  },
);
</script>

<template>
  <TransitionRoot :show="isOpen">
    <Dialog :open="isOpen" as="div" class="relative z-50" @close="handleClose">
      <TransitionChild
        as="template"
        enter="ease-out duration-200"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-150"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-40" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="ease-out duration-200"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-150"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel
              class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl"
              role="dialog"
              aria-modal="true"
              :aria-labelledby="isEditMode ? 'modal-title-edit' : 'modal-title-create'"
            >
              <h2
                :id="isEditMode ? 'modal-title-edit' : 'modal-title-create'"
                class="text-xl font-bold text-gray-900 mb-6"
              >
                {{ isEditMode ? 'Edit Account' : 'Create New Account' }}
              </h2>

              <form class="space-y-4" @submit.prevent="submitForm">
                <div v-if="submitError" class="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p class="text-sm text-red-700">{{ submitError }}</p>
                </div>

                <div>
                  <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
                    Account Name
                  </label>
                  <input
                    id="name"
                    v-model="form.name"
                    type="text"
                    placeholder="e.g., Salary Card, Savings Account"
                    class="w-full px-3 py-2 text-sm border border-neutral-300 rounded-lg bg-neutral-50 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none transition"
                    :aria-invalid="!!errors.name"
                  />
                  <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Account Type</label>
                  <Listbox v-model="form.type">
                    <div class="relative">
                      <ListboxButton
                        class="w-full flex items-center justify-between gap-2 px-3 py-2 text-sm border border-neutral-300 rounded-lg bg-neutral-50 hover:bg-white hover:border-neutral-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition text-left"
                        :aria-invalid="!!errors.type"
                      >
                        <span class="truncate text-neutral-800">{{ selectedTypeLabel }}</span>
                        <ChevronDownIcon class="size-4 text-neutral-400 shrink-0" />
                      </ListboxButton>
                      <ListboxOptions
                        class="absolute z-20 mt-1 w-full rounded-lg border border-neutral-200 bg-white shadow-lg overflow-hidden focus:outline-none"
                      >
                        <ListboxOption
                          v-for="type in ACCOUNT_TYPES"
                          :key="type.value"
                          v-slot="{ active, selected }"
                          :value="type.value"
                        >
                          <li
                            :class="[
                              'flex items-center justify-between px-3 py-2 text-sm cursor-pointer select-none',
                              active ? 'bg-blue-50 text-blue-700' : 'text-neutral-800',
                            ]"
                          >
                            <span>{{ type.label }}</span>
                            <CheckIcon v-if="selected" class="size-4 text-blue-600 shrink-0" />
                          </li>
                        </ListboxOption>
                      </ListboxOptions>
                    </div>
                  </Listbox>
                  <p v-if="errors.type" class="mt-1 text-sm text-red-600">{{ errors.type }}</p>
                </div>

                <div>
                  <label for="balance" class="block text-sm font-medium text-gray-700 mb-1">
                    {{ isEditMode ? 'Current Balance' : 'Initial Balance' }}
                  </label>
                  <div class="relative">
                    <span
                      class="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500 font-medium"
                      >$</span
                    >
                    <input
                      id="balance"
                      v-model="form.balance"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      class="w-full pl-7 pr-3 py-2 text-sm border border-neutral-300 rounded-lg bg-neutral-50 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none transition"
                      :aria-invalid="!!errors.balance"
                    />
                  </div>
                  <p v-if="errors.balance" class="mt-1 text-sm text-red-600">
                    {{ errors.balance }}
                  </p>
                </div>

                <div class="flex gap-2 justify-end pt-4">
                  <button
                    type="button"
                    class="px-4 py-2 text-sm font-medium text-gray-700 border border-neutral-300 rounded-lg hover:bg-neutral-50 transition"
                    @click="handleClose"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    :disabled="isSaving"
                    class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    {{ isSaving ? 'Saving...' : isEditMode ? 'Update' : 'Create' }}
                  </button>
                </div>
              </form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>
