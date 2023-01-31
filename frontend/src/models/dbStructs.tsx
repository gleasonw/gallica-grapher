export interface GallicaResponse {
  records: GallicaRecord[];
  num_results: string;
}

export interface GallicaRecord {
  paper_title: string;
  paper_code: string;
  url: string;
  date: string;
  term: string;
  context: GallicaContext;
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

export interface GraphData {
  request_id: number;
  data: {
    date: number; //year or unix seconds
    count: number;
  }[];
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