"use client";

import type { AnalysisResult } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ChevronDown, ChevronUp, Search } from "lucide-react";
import { useMemo, useState } from "react";

const SENTIMENT_STYLES: Record<string, string> = {
  Positivo: "bg-emerald-950/70 text-emerald-300 ring-1 ring-emerald-800/60",
  Neutro: "bg-amber-950/70 text-amber-300 ring-1 ring-amber-800/60",
  Negativo: "bg-red-950/70 text-red-300 ring-1 ring-red-800/60",
};

interface ResultsTableProps {
  results: AnalysisResult[];
}

export function ResultsTable({ results }: ResultsTableProps) {
  const [filter, setFilter] = useState("");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");
  const [page, setPage] = useState(0);
  const pageSize = 10;

  const filtered = useMemo(() => {
    return results.filter((r) => {
      const matchText =
        !filter ||
        r.comentario_original.toLowerCase().includes(filter.toLowerCase()) ||
        r.comentario_lematizado.toLowerCase().includes(filter.toLowerCase());
      const matchSentiment =
        sentimentFilter === "all" || r.sentimiento === sentimentFilter;
      return matchText && matchSentiment;
    });
  }, [results, filter, sentimentFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageResults = filtered.slice(page * pageSize, (page + 1) * pageSize);

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            type="search"
            placeholder="Buscar en comentarios..."
            value={filter}
            onChange={(e) => {
              setFilter(e.target.value);
              setPage(0);
            }}
            className="h-10 w-full rounded-lg border border-border bg-input pl-10 pr-3 text-sm text-foreground placeholder:text-muted"
          />
        </div>
        <select
          value={sentimentFilter}
          onChange={(e) => {
            setSentimentFilter(e.target.value);
            setPage(0);
          }}
          className="h-10 rounded-lg border border-border bg-input px-3 text-sm text-foreground"
          aria-label="Filtrar por sentimiento"
        >
          <option value="all">Todos los sentimientos</option>
          <option value="Positivo">Positivo</option>
          <option value="Neutro">Neutro</option>
          <option value="Negativo">Negativo</option>
        </select>
      </div>

      <div className="overflow-x-auto rounded-lg border border-border bg-surface">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-surface-muted">
            <tr>
              <th className="px-4 py-3 font-medium text-muted">Comentario original</th>
              <th className="px-4 py-3 font-medium text-muted">Procesado</th>
              <th className="px-4 py-3 font-medium text-muted">Lematizado</th>
              <th className="px-4 py-3 font-medium text-muted">Sentimiento</th>
              <th className="px-4 py-3 font-medium text-muted">Confianza</th>
            </tr>
          </thead>
          <tbody>
            {pageResults.map((row, i) => (
              <tr key={i} className="border-t border-border">
                <td className="max-w-xs px-4 py-3 align-top text-foreground" title={row.comentario_original}>
                  {row.comentario_original}
                </td>
                <td className="max-w-xs px-4 py-3 align-top text-muted">
                  {row.comentario_procesado || "—"}
                </td>
                <td className="max-w-xs px-4 py-3 align-top text-muted">
                  {row.comentario_lematizado || "—"}
                </td>
                <td className="px-4 py-3 align-top">
                  <span
                    className={cn(
                      "inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium",
                      SENTIMENT_STYLES[row.sentimiento] ?? "bg-surface-muted text-muted",
                    )}
                  >
                    {row.sentimiento}
                  </span>
                </td>
                <td className="px-4 py-3 align-top tabular-nums text-foreground">
                  {(row.confianza * 100).toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-sm text-muted">
        <span>
          {filtered.length} resultado{filtered.length !== 1 ? "s" : ""}
        </span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={page === 0}
            onClick={() => setPage((p) => p - 1)}
            className="rounded border border-border bg-surface-muted p-1.5 text-foreground disabled:opacity-40"
            aria-label="Página anterior"
          >
            <ChevronUp className="h-4 w-4 rotate-[-90deg]" />
          </button>
          <span>
            Página {page + 1} de {totalPages}
          </span>
          <button
            type="button"
            disabled={page >= totalPages - 1}
            onClick={() => setPage((p) => p + 1)}
            className="rounded border border-border bg-surface-muted p-1.5 text-foreground disabled:opacity-40"
            aria-label="Página siguiente"
          >
            <ChevronDown className="h-4 w-4 rotate-[-90deg]" />
          </button>
        </div>
      </div>
    </div>
  );
}
