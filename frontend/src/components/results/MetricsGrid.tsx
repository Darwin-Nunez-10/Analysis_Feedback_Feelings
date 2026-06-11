import type { Metrics } from "@/lib/types";
import { Minus, ThumbsDown, ThumbsUp } from "lucide-react";

interface MetricsGridProps {
  metrics: Metrics;
}

function MetricCard({
  label,
  value,
  sub,
  valueClass,
  icon: Icon,
}: {
  label: string;
  value: number | string;
  sub?: string;
  valueClass?: string;
  icon: typeof ThumbsUp;
}) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <div className="flex items-start justify-between">
        <p className="text-sm text-muted">{label}</p>
        <Icon className="h-4 w-4 text-muted" aria-hidden />
      </div>
      <p className={`mt-2 text-2xl font-semibold tabular-nums ${valueClass ?? "text-foreground"}`}>
        {value}
      </p>
      {sub && <p className="mt-1 text-xs text-muted">{sub}</p>}
    </div>
  );
}

export function MetricsGrid({ metrics }: MetricsGridProps) {
  const balance = metrics.pct_positivos - metrics.pct_negativos;

  return (
    <section aria-label="Métricas generales">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <MetricCard label="Total analizados" value={metrics.total} icon={Minus} />
        <MetricCard
          label="Positivos"
          value={metrics.positivos}
          sub={`${metrics.pct_positivos}% del total`}
          valueClass="text-positive"
          icon={ThumbsUp}
        />
        <MetricCard
          label="Neutros"
          value={metrics.neutros}
          sub={`${metrics.pct_neutros}% del total`}
          valueClass="text-neutral"
          icon={Minus}
        />
        <MetricCard
          label="Negativos"
          value={metrics.negativos}
          sub={`${metrics.pct_negativos}% del total`}
          valueClass="text-negative"
          icon={ThumbsDown}
        />
        <MetricCard
          label="Balance positivo − negativo"
          value={`${balance >= 0 ? "+" : ""}${balance.toFixed(1)} pp`}
          sub="Puntos porcentuales"
          icon={Minus}
        />
      </div>
    </section>
  );
}
