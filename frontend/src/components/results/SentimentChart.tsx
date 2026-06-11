"use client";

import type { Metrics } from "@/lib/types";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const COLORS = {
  Positivo: "#34d399",
  Neutro: "#fbbf24",
  Negativo: "#f87171",
};

const CHART = {
  grid: "#334155",
  tick: "#94a3b8",
  tooltipBg: "#1a2234",
  tooltipBorder: "#2d3a4f",
  label: "#e2e8f0",
};

const tooltipStyle = {
  backgroundColor: CHART.tooltipBg,
  border: `1px solid ${CHART.tooltipBorder}`,
  borderRadius: "6px",
  color: CHART.label,
};

interface SentimentChartProps {
  metrics: Metrics;
  variant: "bar" | "pie";
}

function buildData(metrics: Metrics) {
  return [
    { name: "Positivo", value: metrics.positivos, pct: metrics.pct_positivos },
    { name: "Neutro", value: metrics.neutros, pct: metrics.pct_neutros },
    { name: "Negativo", value: metrics.negativos, pct: metrics.pct_negativos },
  ];
}

export function SentimentChart({ metrics, variant }: SentimentChartProps) {
  const data = buildData(metrics);

  if (variant === "pie") {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={110}
            label={({ name, value }) => {
              const item = data.find((d) => d.name === name);
              return `${name}: ${item?.pct ?? value}%`;
            }}
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name as keyof typeof COLORS]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={tooltipStyle}
            formatter={(value) => [`${value ?? 0} comentarios`, "Cantidad"]}
          />
          <Legend wrapperStyle={{ color: CHART.tick }} />
        </PieChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={CHART.grid} />
        <XAxis dataKey="name" tick={{ fontSize: 12, fill: CHART.tick }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: CHART.tick }} />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(value, _name, item) => {
            const pct = (item as { payload?: { pct?: number } })?.payload?.pct ?? 0;
            return [`${value ?? 0} (${pct}%)`, "Comentarios"];
          }}
        />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name as keyof typeof COLORS]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
