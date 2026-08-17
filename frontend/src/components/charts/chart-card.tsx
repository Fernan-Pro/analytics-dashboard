import type { ReactNode } from "react";

import { SectionCard } from "@/components/ui/section-card";
import { cn } from "@/lib/utils";

interface ChartCardProps {
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
  height?: number;
}

/** Contenedor de gráfico: tarjeta con altura fija para ResponsiveContainer. */
export function ChartCard({
  title,
  description,
  children,
  className,
  height = 288,
}: ChartCardProps) {
  return (
    <SectionCard title={title} description={description} className={className}>
      <div className="w-full" style={{ height }}>
        {children}
      </div>
    </SectionCard>
  );
}

export function chartCardGrid({
  className,
  cols = 2,
}: {
  className?: string;
  cols?: 1 | 2 | 3;
} = {}): string {
  return cn(
    "grid gap-4",
    cols >= 2 && "sm:grid-cols-2",
    cols === 3 && "lg:grid-cols-3",
    className,
  );
}