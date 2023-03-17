import { Paper } from "../models/dbStructs";


export interface GraphTicket {
  id: number;
  terms: string[];
  grouping?: "month";
  backend_source?: "gallica" | "pyllica";
  start_date?: number;
  end_date?: number;
  papers?: Paper[];
  link_term?: string;
  link_distance?: number;
  example?: boolean;
}
