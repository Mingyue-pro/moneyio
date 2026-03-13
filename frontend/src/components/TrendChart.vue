<script setup lang="ts">
import { computed } from 'vue';

import type { ChartDataPoint } from '@/api/mock-data';

defineOptions({ name: 'TrendChart' });

interface Props {
  points?: ChartDataPoint[];
  isLoading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  points: () => [],
  isLoading: false,
});

const width = 680;
const height = 240;
const paddingX = 44;
const paddingTop = 16;
const paddingBottom = 28;

const innerHeight = height - paddingTop - paddingBottom;
const innerWidth = width - paddingX * 2;
const bottomY = paddingTop + innerHeight;

const uid = Math.random().toString(36).substring(2, 9);
const incomeGradientId = `income-gradient-${uid}`;
const expenseGradientId = `expense-gradient-${uid}`;
const clipPathId = `chart-area-${uid}`;

const maxValue = computed(() => {
  const values = props.points.flatMap((p) => [p.income, p.expense]);
  return Math.max(...values, 100);
});

const chartPoints = computed(() => {
  if (props.points.length === 0) return [];
  const stepX = innerWidth / Math.max(props.points.length - 1, 1);
  return props.points.map((p, i) => ({
    x: paddingX + i * stepX,
    incomeY: paddingTop + (1 - p.income / maxValue.value) * innerHeight,
    expenseY: paddingTop + (1 - p.expense / maxValue.value) * innerHeight,
    label: p.date.slice(5),
  }));
});

function smoothCurve(pts: Array<{ x: number; y: number }>): string {
  if (pts.length < 2) return '';
  const firstPoint = pts[0];
  if (!firstPoint) return '';
  let d = `M${firstPoint.x},${firstPoint.y}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p1 = pts[i];
    const p2 = pts[i + 1];
    if (!p1 || !p2) continue;
    const p0 = pts[Math.max(0, i - 1)] ?? p1;
    const p3 = pts[Math.min(pts.length - 1, i + 2)] ?? p2;
    const cp1x = p1.x + (p2.x - p0.x) / 6;
    const cp1y = p1.y + (p2.y - p0.y) / 6;
    const cp2x = p2.x - (p3.x - p1.x) / 6;
    const cp2y = p2.y - (p3.y - p1.y) / 6;
    d += ` C${cp1x.toFixed(2)},${cp1y.toFixed(2)} ${cp2x.toFixed(2)},${cp2y.toFixed(2)} ${p2.x.toFixed(2)},${p2.y.toFixed(2)}`;
  }
  return d;
}

const incomeLine = computed(() =>
  smoothCurve(chartPoints.value.map((p) => ({ x: p.x, y: p.incomeY }))),
);
const expenseLine = computed(() =>
  smoothCurve(chartPoints.value.map((p) => ({ x: p.x, y: p.expenseY }))),
);

const incomeArea = computed(() => {
  if (!incomeLine.value || chartPoints.value.length === 0) return '';
  const first = chartPoints.value[0];
  const last = chartPoints.value[chartPoints.value.length - 1];
  if (!first || !last) return '';
  return `${incomeLine.value} L${last.x},${bottomY} L${first.x},${bottomY} Z`;
});

const expenseArea = computed(() => {
  if (!expenseLine.value || chartPoints.value.length === 0) return '';
  const first = chartPoints.value[0];
  const last = chartPoints.value[chartPoints.value.length - 1];
  if (!first || !last) return '';
  return `${expenseLine.value} L${last.x},${bottomY} L${first.x},${bottomY} Z`;
});

const yTicks = computed(() =>
  [0, 0.25, 0.5, 0.75, 1].map((t) => ({
    y: paddingTop + (1 - t) * innerHeight,
    label:
      maxValue.value >= 1000
        ? `$${Math.round((t * maxValue.value) / 1000)}k`
        : `$${Math.round(t * maxValue.value)}`,
  })),
);

const xTicks = computed(() => {
  if (chartPoints.value.length <= 6) return chartPoints.value;
  const step = Math.floor(chartPoints.value.length / 6);
  return chartPoints.value.filter((_, i) => i % step === 0);
});
</script>

<template>
  <section
    class="bg-white rounded-lg border border-gray-200 shadow-sm p-6"
    aria-label="Income and expense trend chart"
  >
    <header class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-lg font-semibold text-gray-900">Income vs Expense Trend</h2>
        <p class="text-sm text-gray-500 mt-0.5">Last 30 Days</p>
      </div>
      <div class="flex items-center gap-4 text-sm text-gray-600">
        <span class="flex items-center gap-2"
          ><span class="w-3 h-3 rounded-full bg-green-600"></span>Income</span
        >
        <span class="flex items-center gap-2"
          ><span class="w-3 h-3 rounded-full bg-red-500"></span>Expense</span
        >
      </div>
    </header>

    <div v-if="isLoading" class="h-60 bg-gray-100 rounded-md animate-pulse"></div>
    <p v-else-if="points.length === 0" class="text-sm text-gray-500 py-10 text-center">
      No trend data available.
    </p>
    <div v-else class="w-full overflow-x-auto">
      <svg
        :viewBox="`0 0 ${width} ${height}`"
        class="min-w-[680px] w-full h-60"
        role="img"
        aria-label="Line chart showing income and expense over 30 days"
      >
        <defs>
          <linearGradient :id="incomeGradientId" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--color-green-600)" stop-opacity="0.25" />
            <stop offset="100%" stop-color="var(--color-green-600)" stop-opacity="0" />
          </linearGradient>
          <linearGradient :id="expenseGradientId" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--color-red-500)" stop-opacity="0.2" />
            <stop offset="100%" stop-color="var(--color-red-500)" stop-opacity="0" />
          </linearGradient>
          <clipPath :id="clipPathId">
            <rect
              :x="paddingX"
              :y="paddingTop"
              :width="width - paddingX * 2"
              :height="innerHeight"
            />
          </clipPath>
        </defs>

        <g v-for="tick in yTicks" :key="tick.y">
          <line
            :x1="paddingX"
            :y1="tick.y"
            :x2="width - paddingX"
            :y2="tick.y"
            class="stroke-gray-100"
            stroke-width="1"
          />
          <text
            :x="paddingX - 6"
            :y="tick.y + 4"
            text-anchor="end"
            class="fill-gray-400 text-[10px]"
          >
            {{ tick.label }}
          </text>
        </g>

        <g :clip-path="`url(#${clipPathId})`">
          <path :d="incomeArea" :fill="`url(#${incomeGradientId})`" />
          <path :d="expenseArea" :fill="`url(#${expenseGradientId})`" />

          <path
            :d="incomeLine"
            fill="none"
            class="stroke-green-600"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <path
            :d="expenseLine"
            fill="none"
            class="stroke-red-500"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </g>

        <text
          v-for="tick in xTicks"
          :key="tick.x"
          :x="tick.x"
          :y="height - 6"
          text-anchor="middle"
          class="fill-gray-400 text-[10px]"
        >
          {{ tick.label }}
        </text>
      </svg>
    </div>
  </section>
</template>
