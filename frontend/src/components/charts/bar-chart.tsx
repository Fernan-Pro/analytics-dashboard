"use client";

import {
  Bar,
  BarChart as RechartsBarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CHART_COLORS, tooltipContentStyle } from "@/lib/utils";

interface BarChartProps<T extends object> {
  data: T[];
  xKey: string;
  barKey: string;
  color?: string;
  height?: number;
  label?: string;
}

export function BarChart<T extends object>({
  data,
  xKey,
  barKey,
  color = CHART_COLORS[0],
  height = 288,
  label,
}: BarChartProps<T>) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsBarChart
        data={data}
        margin={{ top: 8, right: 8, left: -12, bottom: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
        <XAxis
          dataKey={xKey}
          tick={{ fill: "#64748b", fontSize: 12 }}
          tickLine={false}
          axisLine={{ stroke: "#334155" }}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{ fill: "#64748b", fontSize: 12 }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip
          contentStyle={tooltipContentStyle}
          labelStyle={{ color: "#e2e8f0" }}
          cursor={{ fill: "#1e293b", opacity: 0.4 }}
        />
        <Bar
          dataKey={barKey}
          name={label ?? String(barKey)}
          fill={color}
          radius={[6, 6, 0, 0]}
          maxBarSize={48}
        />
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}