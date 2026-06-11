"use client";

import { Button } from "@/components/ui/Button";
import { BookOpen, X } from "lucide-react";

interface HelpPanelProps {
  open: boolean;
  onClose: () => void;
}

export function HelpPanel({ open, onClose }: HelpPanelProps) {
  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/70" onClick={onClose} aria-hidden />
      <aside
        role="dialog"
        aria-labelledby="help-title"
        aria-modal="true"
        className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-border bg-surface shadow-2xl"
      >
        <div className="flex items-center justify-between border-b border-border bg-surface-muted px-6 py-4">
          <h2 id="help-title" className="flex items-center gap-2 text-lg font-semibold text-foreground">
            <BookOpen className="h-5 w-5" aria-hidden />
            Ayuda y documentación
          </h2>
          <Button variant="ghost" size="sm" onClick={onClose} aria-label="Cerrar ayuda">
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto bg-surface px-6 py-4 text-sm leading-relaxed">
          <section className="mb-6">
            <h3 className="mb-2 font-semibold text-foreground">Cómo usar el sistema</h3>
            <ol className="list-decimal space-y-2 pl-5 text-muted">
              <li>Cargue un archivo CSV, Excel o TXT con comentarios de clientes.</li>
              <li>Seleccione la columna que contiene el texto a analizar.</li>
              <li>Revise la vista previa y pulse &quot;Iniciar análisis&quot;.</li>
              <li>Explore métricas, gráficos y la tabla comparativa.</li>
              <li>Descargue los resultados en CSV o Excel si lo necesita.</li>
            </ol>
          </section>

          <section className="mb-6">
            <h3 className="mb-2 font-semibold text-foreground">Formatos admitidos</h3>
            <ul className="list-disc space-y-1 pl-5 text-muted">
              <li>CSV con codificación UTF-8</li>
              <li>Excel (.xlsx, .xls)</li>
              <li>TXT con un comentario por línea</li>
            </ul>
          </section>

          <section className="mb-6">
            <h3 className="mb-2 font-semibold text-foreground">Pipeline de análisis</h3>
            <p className="text-muted">
              El sistema limpia el texto (URLs, números, caracteres especiales), elimina
              stop words, lematiza con spaCy y clasifica el sentimiento con un modelo en
              español. El sentimiento se calcula sobre texto limpio para preservar
              negaciones como &quot;no es bueno&quot;.
            </p>
          </section>

          <section className="mb-6">
            <h3 className="mb-2 font-semibold text-foreground">Solución de problemas</h3>
            <dl className="space-y-3 text-muted">
              <div>
                <dt className="font-medium text-foreground">La API no responde</dt>
                <dd>
                  Inicie el backend: <code>./scripts/run-api.fish</code>
                </dd>
              </div>
              <div>
                <dt className="font-medium text-foreground">Error de modelo spaCy</dt>
                <dd>
                  <code>.venv/bin/python -m spacy download es_core_news_sm</code>
                </dd>
              </div>
              <div>
                <dt className="font-medium text-foreground">Comentarios excluidos</dt>
                <dd>Algunos textos pueden filtrarse si no parecen estar en español.</dd>
              </div>
            </dl>
          </section>

          <section>
            <h3 className="mb-2 font-semibold text-foreground">Proyecto académico</h3>
            <p className="text-muted">
              EIF-4200 Inteligencia Artificial I — Sistema Inteligente de Análisis de
              Feedback y Sentimiento del Cliente.
            </p>
          </section>
        </div>
      </aside>
    </>
  );
}
