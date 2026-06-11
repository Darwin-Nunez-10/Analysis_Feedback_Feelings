import type {
  AnalyzeResponse,
  ApiErrorDetail,
  PreviewResponse,
  SystemStatus,
  ValidationTest,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: ApiErrorDetail | string };
    const detail = data.detail;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object") {
      const msg = detail.message ?? "Error desconocido";
      const sol = detail.solution;
      return sol ? `${msg} ${sol}` : msg;
    }
    return `Error ${response.status}: ${response.statusText}`;
  } catch {
    return `Error ${response.status}: ${response.statusText}`;
  }
}

export async function fetchHealth(): Promise<SystemStatus> {
  const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function previewFile(file: File): Promise<PreviewResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/preview`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function analyzeFile(
  file: File,
  column: string,
  onProgress?: (pct: number) => void,
): Promise<AnalyzeResponse> {
  onProgress?.(10);
  const form = new FormData();
  form.append("file", file);
  form.append("column", column);
  onProgress?.(30);
  const res = await fetch(`${API_BASE}/api/analyze`, { method: "POST", body: form });
  onProgress?.(90);
  if (!res.ok) throw new Error(await parseError(res));
  const data = await res.json();
  onProgress?.(100);
  return data;
}

export async function fetchValidation(): Promise<ValidationTest[]> {
  const res = await fetch(`${API_BASE}/api/validation`);
  if (!res.ok) throw new Error(await parseError(res));
  const data = await res.json();
  return data.tests;
}

export async function downloadExport(
  format: "csv" | "xlsx",
  results: AnalyzeResponse["results"],
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/export/${format}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ results }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.blob();
}

export const ACCEPTED_EXTENSIONS = [".csv", ".xlsx", ".xls", ".txt"];
export const MAX_FILE_SIZE_MB = 10;

export function validateFileClient(file: File): string | null {
  const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
  if (!ACCEPTED_EXTENSIONS.includes(ext)) {
    return `Formato no compatible. Use: ${ACCEPTED_EXTENSIONS.join(", ")}`;
  }
  if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
    return `El archivo supera ${MAX_FILE_SIZE_MB} MB. Reduzca el tamaño e intente de nuevo.`;
  }
  return null;
}
