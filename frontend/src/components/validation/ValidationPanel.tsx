"use client";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { fetchValidation } from "@/lib/api";
import type { ValidationTest } from "@/lib/types";
import { FlaskConical, Loader2 } from "lucide-react";
import { useState } from "react";

export function ValidationPanel() {
  const [tests, setTests] = useState<ValidationTest[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runTests() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchValidation();
      setTests(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al ejecutar pruebas");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FlaskConical className="h-5 w-5" aria-hidden />
          Pruebas de validación
        </CardTitle>
        <CardDescription>
          Ejemplos controlados para evaluar negaciones, ironía y expresiones coloquiales.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button variant="secondary" onClick={runTests} loading={loading}>
          {loading ? "Ejecutando..." : "Ejecutar pruebas de validación"}
        </Button>

        {error && (
          <Alert variant="error" title="Error en las pruebas">
            {error}
          </Alert>
        )}

        {loading && !tests && (
          <div className="flex items-center gap-2 py-4 text-sm text-muted">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            Procesando ejemplos de negación y sarcasmo...
          </div>
        )}

        {tests && (
          <div className="overflow-x-auto rounded-lg border border-border bg-surface">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead className="bg-surface-muted">
                <tr>
                  <th className="px-4 py-3 font-medium text-muted">Texto</th>
                  <th className="px-4 py-3 font-medium text-muted">Tipo</th>
                  <th className="px-4 py-3 font-medium text-muted">Sentimiento</th>
                  <th className="px-4 py-3 font-medium text-muted">Observación</th>
                </tr>
              </thead>
              <tbody>
                {tests.map((t, i) => (
                  <tr key={i} className="border-t border-border">
                    <td className="px-4 py-3 align-top text-foreground">{t.texto_original}</td>
                    <td className="px-4 py-3 align-top text-muted">{t.tipo_prueba}</td>
                    <td className="px-4 py-3 align-top text-foreground">
                      {t.sentimiento}
                      <span className="ml-1 text-xs text-muted">
                        ({(t.confianza * 100).toFixed(0)}%)
                      </span>
                    </td>
                    <td className="max-w-sm px-4 py-3 align-top text-muted">{t.observacion}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
