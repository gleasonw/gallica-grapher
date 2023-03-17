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
export type Page = "graph" | "context" | "info";

export const initTickets = [
  {
    id: 0,
    terms: ["brazza"],
    grouping: "month",
    example: true,
  },
  {
    id: 1,
    terms: ["congo"],
    grouping: "month",
    example: true,
  },
  {
    id: -1,
    terms: ["coloniale"],
    grouping: "month",
    example: true,
  },
] as GraphTicket[];
