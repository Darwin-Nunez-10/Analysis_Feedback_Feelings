import type { WorkflowStep } from "@/lib/types";
import { cn } from "@/lib/utils";
import { BarChart3, FileSearch, Settings2, Upload } from "lucide-react";

const STEPS: { id: WorkflowStep; label: string; icon: typeof Upload }[] = [
  { id: "upload", label: "Cargar datos", icon: Upload },
  { id: "configure", label: "Configurar", icon: Settings2 },
  { id: "analyze", label: "Analizar", icon: FileSearch },
  { id: "results", label: "Resultados", icon: BarChart3 },
];

interface StepIndicatorProps {
  current: WorkflowStep;
}

const order: WorkflowStep[] = ["upload", "configure", "analyze", "results"];

export function StepIndicator({ current }: StepIndicatorProps) {
  const currentIdx = order.indexOf(current);

  return (
    <nav aria-label="Progreso del análisis" className="w-full">
      <ol className="flex items-center justify-between gap-2">
        {STEPS.map((step, idx) => {
          const Icon = step.icon;
          const isComplete = idx < currentIdx;
          const isCurrent = step.id === current;
          return (
            <li key={step.id} className="flex flex-1 items-center">
              <div
                className={cn(
                  "flex flex-col items-center gap-1.5 text-center sm:flex-row sm:gap-2 sm:text-left",
                  idx <= currentIdx ? "text-foreground" : "text-muted",
                )}
              >
                <span
                  className={cn(
                    "flex h-9 w-9 items-center justify-center rounded-full border-2 text-sm font-medium transition-colors",
                    isComplete && "border-accent bg-accent text-white",
                    isCurrent && !isComplete && "border-accent bg-surface text-accent",
                    !isComplete && !isCurrent && "border-border bg-surface-muted",
                  )}
                  aria-current={isCurrent ? "step" : undefined}
                >
                  {isComplete ? (
                    <span aria-hidden className="text-xs">
                      {idx + 1}
                    </span>
                  ) : (
                    <Icon className="h-4 w-4" aria-hidden />
                  )}
                </span>
                <span className={cn("text-xs font-medium sm:text-sm", isCurrent && "font-semibold")}>
                  {step.label}
                </span>
              </div>
              {idx < STEPS.length - 1 && (
                <div
                  className={cn(
                    "mx-2 hidden h-0.5 flex-1 sm:block",
                    idx < currentIdx ? "bg-accent" : "bg-border",
                  )}
                  aria-hidden
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
