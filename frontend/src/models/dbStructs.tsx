export interface GallicaResponse {
  records: VolumeRecord[];
  num_results: string;
  origin_urls: string[];
}

export interface VolumeRecord {
  paper_title: string;
  paper_code: string;
  ocr_quality: number;
  author: string;
  ark: string;
  url: string;
  date: string;
  terms: string[];
  context: ContextRow[];
}

export interface ContextRow {
  pivot: string;
  left_context: string;
  right_context: string;
  page_url: string;
  page: number | null;
}

export interface Paper {
  title: string;
  code: string;
  start_date: string;
  end_date: string;
}

export interface ProgressType {
  num_results_discovered: number;
  num_requests_to_send: number;
  num_requests_sent: number;
  estimate_seconds_to_completion: number;
  random_paper: string;
  random_text: string;
  state: "too_many_records" | "completed" | "error" | "no_records" | "running";
  backend_source: "gallica" | "pyllica";
}

export interface FrequentTerm {
  term: string;
  count: number;
}

export interface GraphData {
  request_id: number;
  data: [number, number][];
  name: string;
}

export interface GallicaContext {
  num_results: number;
  pages: GallicaPage[];
  ark: string;
}

export interface GallicaPage {
  page: string;
  context: string;
}
