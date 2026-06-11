import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import { Columns3 } from "lucide-react";

interface ColumnSelectorProps {
  columns: string[];
  textColumns: string[];
  value: string;
  onChange: (column: string) => void;
  disabled?: boolean;
}

export function ColumnSelector({
  columns,
  textColumns,
  value,
  onChange,
  disabled,
}: ColumnSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Columns3 className="h-5 w-5" aria-hidden />
          Columna de comentarios
        </CardTitle>
        <CardDescription>
          Indique qué columna contiene el texto a analizar. Se resaltan las columnas con texto
          detectado automáticamente.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <fieldset disabled={disabled} className="space-y-2">
          <legend className="sr-only">Seleccionar columna de comentarios</legend>
          {columns.map((col) => {
            const isRecommended = textColumns.includes(col);
            return (
              <label
                key={col}
                className={cn(
                  "flex cursor-pointer items-center gap-3 rounded-lg border px-4 py-3 transition-colors",
                  value === col
                    ? "border-accent bg-accent/15"
                    : "border-border bg-surface-muted hover:bg-surface-highlight",
                  disabled && "cursor-not-allowed opacity-50",
                )}
              >
                <input
                  type="radio"
                  name="comment-column"
                  value={col}
                  checked={value === col}
                  onChange={() => onChange(col)}
                  className="h-4 w-4 accent-accent"
                />
                <span className="text-sm font-medium text-foreground">{col}</span>
                {isRecommended && (
                  <span className="ml-auto text-xs text-muted">Texto detectado</span>
                )}
              </label>
            );
          })}
        </fieldset>
      </CardContent>
    </Card>
  );
}
