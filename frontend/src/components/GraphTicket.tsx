import { Paper } from "../models/dbStructs";


export interface GraphTicket {
  id: number;
  terms: string[];
  start_date?: number;
  end_date?: number;
  example?: boolean;
}
