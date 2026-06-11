import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import type { PreviewResponse } from "@/lib/types";

interface DataPreviewProps {
  preview: PreviewResponse;
  selectedColumn: string;
}

export function DataPreview({ preview, selectedColumn }: DataPreviewProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Vista previa de datos</CardTitle>
        <CardDescription>
          {preview.filename} — {preview.row_count} filas. Mostrando las primeras 20.
        </CardDescription>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full min-w-[480px] text-left text-sm">
          <thead>
            <tr className="border-b border-border bg-surface-muted">
              {preview.columns.map((col) => (
                <th
                  key={col}
                  className={`px-3 py-2 font-medium ${
                    col === selectedColumn
                      ? "bg-accent/20 text-accent"
                      : "text-muted"
                  }`}
                >
                  {col}
                  {col === selectedColumn && (
                    <span className="ml-1 text-xs font-normal">(seleccionada)</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-surface">
            {preview.preview.map((row, i) => (
              <tr key={i} className="border-b border-border last:border-0">
                {preview.columns.map((col) => (
                  <td
                    key={col}
                    className={`max-w-xs truncate px-3 py-2 text-foreground ${
                      col === selectedColumn ? "bg-accent/10" : ""
                    }`}
                    title={row[col]}
                  >
                    {row[col]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
