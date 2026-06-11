"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface WordFrequencyChartProps {
  data: { Palabra: string; Frecuencia: number }[];
  limit?: number;
}

export function WordFrequencyChart({ data, limit = 10 }: WordFrequencyChartProps) {
  const chartData = data.slice(0, limit).map((d) => ({
    word: d.Palabra,
    count: d.Frecuencia,
  }));

  if (chartData.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted">
        No hay palabras frecuentes disponibles tras la lematización.
      </p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(240, chartData.length * 32)}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
        <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12, fill: "#94a3b8" }} />
        <YAxis type="category" dataKey="word" width={100} tick={{ fontSize: 12, fill: "#94a3b8" }} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1a2234",
            border: "1px solid #2d3a4f",
            borderRadius: "6px",
            color: "#e2e8f0",
          }}
          formatter={(value) => [`${value ?? 0} ocurrencias`, "Frecuencia"]}
        />
        <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
