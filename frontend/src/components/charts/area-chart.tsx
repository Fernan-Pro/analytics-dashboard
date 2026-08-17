"use client";

import {
  Area,
  AreaChart as RechartsAreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CHART_COLORS, tooltipContentStyle } from "@/lib/utils";

interface AreaChartProps<T extends object> {
  data: T[];
  xKey: string;
  series: { key: string; label: string; color?: string }[];
  height?: number;
}

export function AreaChart<T extends object>({
  data,
  xKey,
  series,
  height = 288,
}: AreaChartProps<T>) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsAreaChart
        data={data}
        margin={{ top: 8, right: 8, left: -12, bottom: 0 }}
      >
        <defs>
          {series.map((s, i) => {
            const color = s.color ?? CHART_COLORS[i % CHART_COLORS.length];
            const id = `grad-${String(s.key)}`;
            return (
              <linearGradient key={id} id={id} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.35} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            );
          })}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
        <XAxis
          dataKey={xKey}
          tick={{ fill: "#64748b", fontSize: 12 }}
          tickLine={false}
          axisLine={{ stroke: "#334155" }}
        />
        <YAxis
          tick={{ fill: "#64748b", fontSize: 12 }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip contentStyle={tooltipContentStyle} labelStyle={{ color: "#e2e8f0" }} />
        <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
        {series.map((s, i) => {
          const color = s.color ?? CHART_COLORS[i % CHART_COLORS.length];
          return (
            <Area
              key={String(s.key)}
              type="monotone"
              dataKey={String(s.key)}
              name={s.label}
              stroke={color}
              strokeWidth={2}
              fill={`url(#grad-${String(s.key)})`}
            />
          );
        })}
      </RechartsAreaChart>
    </ResponsiveContainer>
  );
}