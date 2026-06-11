"use client";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { HelpPanel } from "@/components/help/HelpPanel";
import { StepIndicator } from "@/components/layout/StepIndicator";
import { MetricsGrid } from "@/components/results/MetricsGrid";
import { ResultsTable } from "@/components/results/ResultsTable";
import { SentimentChart } from "@/components/results/SentimentChart";
import { WordFrequencyChart } from "@/components/results/WordFrequencyChart";
import { ColumnSelector } from "@/components/upload/ColumnSelector";
import { DataPreview } from "@/components/upload/DataPreview";
import { FileUpload } from "@/components/upload/FileUpload";
import {
  analyzeFile,
  downloadExport,
  fetchHealth,
  previewFile,
} from "@/lib/api";
import type {
  AnalyzeResponse,
  PreviewResponse,
  SystemStatus,
  WorkflowStep,
} from "@/lib/types";
import {
  Activity,
  ArrowLeft,
  BarChart2,
  CircleHelp,
  Download,
  FileSpreadsheet,
  Play,
  RotateCcw,
  Server,
} from "lucide-react";
import dynamic from "next/dynamic";
import Image from "next/image";
import { useCallback, useEffect, useState } from "react";

const LazyValidationPanel = dynamic(
  () => import("@/components/validation/ValidationPanel").then((m) => m.ValidationPanel),
  { loading: () => <p className="text-sm text-muted">Cargando pruebas...</p> },
);

export function Dashboard() {
  const [step, setStep] = useState<WorkflowStep>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [selectedColumn, setSelectedColumn] = useState("");
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [chartVariant, setChartVariant] = useState<"bar" | "pie">("bar");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [helpOpen, setHelpOpen] = useState(false);
  const [health, setHealth] = useState<SystemStatus | null>(null);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() =>
        setHealth({
          status: "degraded",
          spacy_loaded: false,
          spacy_model: null,
          sentiment_loaded: false,
          sentiment_model: null,
        }),
      );
  }, []);

  const resetAll = useCallback(() => {
    setStep("upload");
    setFile(null);
    setPreview(null);
    setSelectedColumn("");
    setAnalysis(null);
    setError(null);
    setProgress(0);
  }, []);

  const handleFileSelect = useCallback(async (selected: File) => {
    setFile(selected);
    setError(null);
    setLoading(true);
    setProgress(20);
    try {
      const data = await previewFile(selected);
      setPreview(data);
      setSelectedColumn(data.suggested_column ?? data.text_columns[0] ?? data.columns[0] ?? "");
      setStep("configure");
      setProgress(100);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al previsualizar");
      setFile(null);
    } finally {
      setLoading(false);
      setProgress(0);
    }
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!file || !selectedColumn) return;
    setError(null);
    setLoading(true);
    setStep("analyze");
    setProgress(0);
    try {
      const data = await analyzeFile(file, selectedColumn, setProgress);
      setAnalysis(data);
      setStep("results");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error durante el análisis");
      setStep("configure");
    } finally {
      setLoading(false);
    }
  }, [file, selectedColumn]);

  async function handleExport(format: "csv" | "xlsx") {
    if (!analysis) return;
    try {
      const blob = await downloadExport(format, analysis.results);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `resultados_sentimiento.${format === "csv" ? "csv" : "xlsx"}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al exportar");
    }
  }

  const apiReady = health?.spacy_loaded && health?.sentiment_loaded;

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-30 border-b border-border bg-surface/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <div>
            <h1 className="text-lg font-semibold text-foreground sm:text-xl">
              Análisis de Feedback y Sentimiento
            </h1>
            <p className="text-xs text-muted sm:text-sm">
              EIF-4200 · Dashboard gerencial de comentarios de clientes
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="hidden items-center gap-1.5 rounded-full border border-border bg-surface-muted px-3 py-1.5 text-xs sm:flex"
              title="Estado del backend"
            >
              <Server className="h-3.5 w-3.5" aria-hidden />
              <span className={apiReady ? "text-emerald-400" : "text-amber-400"}>
                {apiReady ? "Sistema listo" : "Backend pendiente"}
              </span>
            </div>
            <Button variant="ghost" size="sm" onClick={() => setHelpOpen(true)}>
              <CircleHelp className="h-4 w-4" />
              <span className="hidden sm:inline">Ayuda</span>
            </Button>
            {(step !== "upload" || analysis) && (
              <Button variant="secondary" size="sm" onClick={resetAll}>
                <RotateCcw className="h-4 w-4" />
                <span className="hidden sm:inline">Reiniciar</span>
              </Button>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6">
        {!apiReady && (
          <Alert variant="warning" title="Backend no disponible">
            Inicie la API Python antes de analizar:{" "}
            <code className="text-xs">./scripts/run-api.fish</code> o{" "}
            <code className="text-xs">./scripts/run-api.sh</code>
          </Alert>
        )}

        <StepIndicator current={step} />

        {loading && (
          <div className="space-y-2" role="status" aria-live="polite">
            <div className="flex items-center gap-2 text-sm text-muted">
              <Activity className="h-4 w-4 animate-pulse" aria-hidden />
              {step === "analyze" ? "Analizando comentarios..." : "Procesando archivo..."}
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-surface-highlight">
              <div
                className="h-full bg-accent transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {error && (
          <Alert variant="error" title="Se produjo un problema">
            {error}
          </Alert>
        )}

        {(step === "upload" || step === "configure") && (
          <div className="grid gap-6 lg:grid-cols-2">
            <FileUpload
              file={file}
              onFileSelect={handleFileSelect}
              onClear={() => {
                setFile(null);
                setPreview(null);
                setStep("upload");
              }}
              disabled={loading}
            />
            {preview && (
              <ColumnSelector
                columns={preview.columns}
                textColumns={preview.text_columns}
                value={selectedColumn}
                onChange={setSelectedColumn}
                disabled={loading}
              />
            )}
          </div>
        )}

        {preview && step !== "results" && (
          <>
            <DataPreview preview={preview} selectedColumn={selectedColumn} />
            <div className="flex flex-wrap gap-3">
              {step === "configure" && (
                <>
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={handleAnalyze}
                    loading={loading}
                    disabled={!selectedColumn || !apiReady}
                  >
                    <Play className="h-4 w-4" />
                    Iniciar análisis
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setPreview(null);
                      setFile(null);
                      setStep("upload");
                    }}
                    disabled={loading}
                  >
                    <ArrowLeft className="h-4 w-4" />
                    Cambiar archivo
                  </Button>
                </>
              )}
            </div>
          </>
        )}

        {analysis && step === "results" && (
          <div className="space-y-8">
            {analysis.excluded_count > 0 && (
              <Alert variant="warning" title="Comentarios excluidos">
                {analysis.excluded_count} comentario(s) posiblemente en idioma no soportado
                fueron omitidos.
                {analysis.excluded_samples.length > 0 && (
                  <ul className="mt-2 list-disc pl-5 text-xs">
                    {analysis.excluded_samples.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                )}
              </Alert>
            )}

            <section>
              <h2 className="mb-4 text-lg font-semibold text-foreground">Métricas generales</h2>
              <MetricsGrid metrics={analysis.metrics} />
            </section>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between gap-4">
                <div>
                  <CardTitle>Distribución de sentimiento</CardTitle>
                  <CardDescription>
                    Proporción de comentarios positivos, neutros y negativos.
                  </CardDescription>
                </div>
                <div className="flex rounded-lg border border-border bg-surface-muted p-0.5">
                  <button
                    type="button"
                    onClick={() => setChartVariant("bar")}
                    className={`rounded px-3 py-1.5 text-xs font-medium transition-colors ${
                      chartVariant === "bar"
                        ? "bg-accent text-white"
                        : "text-muted hover:text-foreground"
                    }`}
                  >
                    <BarChart2 className="inline h-3.5 w-3.5" /> Barras
                  </button>
                  <button
                    type="button"
                    onClick={() => setChartVariant("pie")}
                    className={`rounded px-3 py-1.5 text-xs font-medium transition-colors ${
                      chartVariant === "pie"
                        ? "bg-accent text-white"
                        : "text-muted hover:text-foreground"
                    }`}
                  >
                    Circular
                  </button>
                </div>
              </CardHeader>
              <CardContent>
                <SentimentChart metrics={analysis.metrics} variant={chartVariant} />
              </CardContent>
            </Card>

            {analysis.wordcloud_base64 && (
              <Card>
                <CardHeader>
                  <CardTitle>Nube de palabras</CardTitle>
                  <CardDescription>
                    Términos más frecuentes del texto lematizado (sin stop words).
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex justify-center bg-surface-muted">
                  <Image
                    src={`data:image/png;base64,${analysis.wordcloud_base64}`}
                    alt="Nube de palabras del análisis"
                    width={800}
                    height={400}
                    className="max-w-full rounded-lg border border-border"
                    unoptimized
                  />
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Palabras clave más frecuentes</CardTitle>
                <CardDescription>Top 10 términos tras lematización.</CardDescription>
              </CardHeader>
              <CardContent>
                <WordFrequencyChart data={analysis.word_frequencies} limit={10} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tabla comparativa</CardTitle>
                <CardDescription>
                  Texto original, procesado, lematizado, sentimiento y confianza del modelo.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResultsTable results={analysis.results} />
              </CardContent>
            </Card>

            <div className="flex flex-wrap gap-3">
              <Button variant="primary" onClick={() => handleExport("csv")}>
                <Download className="h-4 w-4" />
                Descargar CSV
              </Button>
              <Button variant="secondary" onClick={() => handleExport("xlsx")}>
                <FileSpreadsheet className="h-4 w-4" />
                Descargar Excel
              </Button>
              <Button variant="ghost" onClick={() => setStep("configure")}>
                <ArrowLeft className="h-4 w-4" />
                Volver a configuración
              </Button>
            </div>
          </div>
        )}

        <section className="border-t border-border pt-8">
          <LazyValidationPanel />
        </section>
      </main>

      <HelpPanel open={helpOpen} onClose={() => setHelpOpen(false)} />
    </div>
  );
}
