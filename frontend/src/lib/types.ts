export interface SystemStatus {
  status: string;
  spacy_loaded: boolean;
  spacy_model: string | null;
  sentiment_loaded: boolean;
  sentiment_model: string | null;
}

export interface PreviewResponse {
  filename: string;
  row_count: number;
  columns: string[];
  text_columns: string[];
  preview: Record<string, string>[];
  suggested_column: string | null;
}

export interface Metrics {
  total: number;
  positivos: number;
  neutros: number;
  negativos: number;
  pct_positivos: number;
  pct_neutros: number;
  pct_negativos: number;
}

export interface AnalysisResult {
  comentario_original: string;
  comentario_procesado: string;
  comentario_lematizado: string;
  sentimiento: string;
  confianza: number;
  probabilidades: Record<string, number>;
}

export interface AnalyzeResponse {
  metrics: Metrics;
  results: AnalysisResult[];
  word_frequencies: { Palabra: string; Frecuencia: number }[];
  wordcloud_base64: string | null;
  excluded_count: number;
  excluded_samples: string[];
  analyzed_count: number;
  models: { spacy: string | null; sentiment: string };
}

export interface ValidationTest {
  texto_original: string;
  tipo_prueba: string;
  expectativa: string;
  sentimiento: string;
  confianza: number;
  observacion: string;
}

export interface ApiErrorDetail {
  message?: string;
  solution?: string;
  detail?: { message?: string; solution?: string };
}

export type WorkflowStep = "upload" | "configure" | "analyze" | "results";
