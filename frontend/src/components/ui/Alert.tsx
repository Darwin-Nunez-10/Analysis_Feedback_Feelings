import { cn } from "@/lib/utils";
import { AlertCircle, CheckCircle2, Info, XCircle } from "lucide-react";

type AlertVariant = "info" | "success" | "warning" | "error";

const config: Record<AlertVariant, { icon: typeof Info; classes: string }> = {
  info: { icon: Info, classes: "border-blue-800/70 bg-blue-950/50 text-blue-200" },
  success: { icon: CheckCircle2, classes: "border-emerald-800/70 bg-emerald-950/50 text-emerald-200" },
  warning: { icon: AlertCircle, classes: "border-amber-800/70 bg-amber-950/50 text-amber-200" },
  error: { icon: XCircle, classes: "border-red-800/70 bg-red-950/50 text-red-200" },
};

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function Alert({ variant = "info", title, children, className }: AlertProps) {
  const { icon: Icon, classes } = config[variant];
  return (
    <div
      role="alert"
      className={cn("flex gap-3 rounded-lg border p-4 text-sm", classes, className)}
    >
      <Icon className="mt-0.5 h-5 w-5 shrink-0" aria-hidden />
      <div>
        {title && <p className="font-medium">{title}</p>}
        <div className={title ? "mt-1" : ""}>{children}</div>
      </div>
    </div>
  );
}
