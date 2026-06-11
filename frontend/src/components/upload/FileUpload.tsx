"use client";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { ACCEPTED_EXTENSIONS, validateFileClient } from "@/lib/api";
import { cn } from "@/lib/utils";
import { FileText, Upload, X } from "lucide-react";
import { useCallback, useRef, useState } from "react";

interface FileUploadProps {
  file: File | null;
  onFileSelect: (file: File) => void;
  onClear: () => void;
  disabled?: boolean;
}

export function FileUpload({ file, onFileSelect, onClear, disabled }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(
    (selected: File) => {
      const validationError = validateFileClient(selected);
      if (validationError) {
        setError(validationError);
        return;
      }
      setError(null);
      onFileSelect(selected);
    },
    [onFileSelect],
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (disabled) return;
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFile(dropped);
    },
    [disabled, handleFile],
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Cargar comentarios de clientes</CardTitle>
        <CardDescription>
          Seleccione un archivo con reseñas o feedback. Formatos admitidos:{" "}
          {ACCEPTED_EXTENSIONS.join(", ")}.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!file ? (
          <div
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
            }}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => !disabled && inputRef.current?.click()}
            className={cn(
              "flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-12 transition-colors",
              dragOver
                ? "border-accent bg-accent/10"
                : "border-border bg-surface-muted hover:border-surface-highlight hover:bg-surface-highlight/50",
              disabled && "cursor-not-allowed opacity-50",
            )}
          >
            <Upload className="mb-3 h-10 w-10 text-muted" aria-hidden />
            <p className="text-sm font-medium text-foreground">
              Arrastre su archivo aquí o haga clic para seleccionar
            </p>
            <p className="mt-1 text-xs text-muted">Tamaño máximo: 10 MB</p>
            <input
              ref={inputRef}
              type="file"
              accept={ACCEPTED_EXTENSIONS.join(",")}
              className="sr-only"
              disabled={disabled}
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFile(f);
              }}
            />
          </div>
        ) : (
          <div className="flex items-center justify-between rounded-lg border border-border bg-surface-muted px-4 py-3">
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8 text-accent" aria-hidden />
              <div>
                <p className="text-sm font-medium text-foreground">{file.name}</p>
                <p className="text-xs text-muted">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClear}
              disabled={disabled}
              aria-label="Quitar archivo seleccionado"
            >
              <X className="h-4 w-4" />
              Quitar
            </Button>
          </div>
        )}

        {error && (
          <Alert variant="error" title="No se pudo cargar el archivo">
            {error}
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
