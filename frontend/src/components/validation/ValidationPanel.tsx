"use client";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { fetchValidation } from "@/lib/api";
import type { ValidationTest } from "@/lib/types";
import { cn } from "@/lib/utils";
import { CheckCircle2, FlaskConical, Loader2, XCircle } from "lucide-react";
import { useState } from "react";

const SENTIMENT_STYLES: Record<string, string> = {
  Positivo: "bg-emerald-950/70 text-emerald-300 ring-1 ring-emerald-800/60",
  Neutro: "bg-amber-950/70 text-amber-300 ring-1 ring-amber-800/60",
  Negativo: "bg-red-950/70 text-red-300 ring-1 ring-red-800/60",
};

function AciertoIcon({ acierto }: { acierto: ValidationTest["acierto"] }) {
  if (acierto === "correcto") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-950/70 px-2.5 py-0.5 text-xs font-medium text-emerald-300 ring-1 ring-emerald-800/60">
        <CheckCircle2 className="h-3.5 w-3.5" aria-hidden />
        Correcto
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-red-950/70 px-2.5 py-0.5 text-xs font-medium text-red-300 ring-1 ring-red-800/60">
      <XCircle className="h-3.5 w-3.5" aria-hidden />
      Incorrecto
    </span>
  );
}

function Summary({ tests }: { tests: ValidationTest[] }) {
  const correctos = tests.filter((t) => t.acierto === "correcto").length;
  const pct = Math.round((correctos / tests.length) * 100);
  return (
    <div className="flex flex-wrap items-center gap-4 rounded-lg border border-border bg-surface-muted px-4 py-3 text-sm">
      <span className="text-muted">Resultados:</span>
      <span className="font-medium text-emerald-300">{correctos} correctos</span>
      <span className="font-medium text-red-300">{tests.length - correctos} incorrectos</span>
      <span className="ml-auto font-semibold text-foreground">{pct}% de precisión</span>
    </div>
  );
}

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
          Evaluación y Reporte — Pruebas de precisión del modelo
        </CardTitle>
        <CardDescription>
          Cuadro comparativo de negaciones, sarcasmo e intensificadores. Evalúa si el modelo
          detecta correctamente la polaridad en casos lingüísticos complejos.
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
          <div className="space-y-4">
            <Summary tests={tests} />

            <div className="overflow-x-auto rounded-lg border border-border bg-surface">
              <table className="w-full min-w-[860px] text-left text-sm">
                <thead className="bg-surface-muted">
                  <tr>
                    <th className="px-4 py-3 font-medium text-muted">Texto de prueba</th>
                    <th className="px-4 py-3 font-medium text-muted">Tipo de caso</th>
                    <th className="px-4 py-3 font-medium text-muted">Expectativa</th>
                    <th className="px-4 py-3 font-medium text-muted">Sentimiento obtenido</th>
                    <th className="px-4 py-3 font-medium text-muted">Resultado</th>
                    <th className="px-4 py-3 font-medium text-muted">Observación</th>
                  </tr>
                </thead>
                <tbody>
                  {tests.map((t, i) => (
                    <tr
                      key={i}
                      className={cn(
                        "border-t border-border",
                        t.acierto === "incorrecto" && "bg-red-950/10",
                      )}
                    >
                      <td className="max-w-[200px] px-4 py-3 align-top font-medium text-foreground">
                        {t.texto_original}
                      </td>
                      <td className="px-4 py-3 align-top text-muted">{t.tipo_prueba}</td>
                      <td className="px-4 py-3 align-top text-muted italic">{t.expectativa}</td>
                      <td className="px-4 py-3 align-top">
                        <span
                          className={cn(
                            "inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium",
                            SENTIMENT_STYLES[t.sentimiento] ?? "bg-surface-muted text-muted",
                          )}
                        >
                          {t.sentimiento}
                        </span>
                        <span className="ml-1.5 text-xs text-muted">
                          {(t.confianza * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="px-4 py-3 align-top">
                        <AciertoIcon acierto={t.acierto} />
                      </td>
                      <td className="max-w-xs px-4 py-3 align-top text-xs text-muted">
                        {t.observacion}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="text-xs text-muted">
              Modelo: pysentimiento/robertuito (RoBERTa entrenado en Twitter en español).
              Las expectativas con &ldquo;o&rdquo; admiten cualquiera de las opciones como resultado correcto.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
