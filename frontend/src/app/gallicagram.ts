import { DataFrame, toJSON } from "danfojs-node";
import * as Papa from "papaparse";
import { GraphData } from "./components/models/dbStructs";

type CorpusType = "lemonde" | "livres" | "presse";
type ResolutionType = "default" | "annee" | "mois";

type Ticket = {
  term: string;
  year?: number;
  end_year?: number;
  codes?: string[];
  source: CorpusType;
  grouping?: ResolutionType;
  smoothing?: number;
};

type GallicaGramRow = {
  n_sum: number;
  gram: string;
  annee: string;
  mois: string;
  total_sum: number;
  ratio: number;
};

export async function getSeries(
  { term, year, end_year, grouping, smoothing, source }: Ticket,
  onNoRecordsFound: () => void
): Promise<GraphData | undefined> {
  if (!term) {
    return;
  }
  const debut = year ?? 1789;
  const fin = end_year ?? 1950;

  try {
    const response = await fetch(
      `https://shiny.ens-paris-saclay.fr/guni/query?corpus=${source}&mot=${term}&from=${debut}&to=${fin}&resolution=${grouping}`
    );
    const stringResponse = await response.text();
    const parsedCSV = Papa.parse(stringResponse, { header: true });
    let dataFrame = new DataFrame(parsedCSV.data, {
      columns: ["n", "gram", "annee", "mois", "total"],
    });
    let groupedFrame: DataFrame | null = null;
    if (grouping === "mois" && source !== "livres") {
      groupedFrame = dataFrame
        .groupby(["annee", "mois", "gram"])
        .agg({ n: "sum", total: "sum" })
        .resetIndex();
    }
    if (grouping === "annee") {
      groupedFrame = dataFrame
        .groupby(["annee", "gram"])
        .agg({ n: "sum", total: "sum" })
        .resetIndex();
    }
    let rows = toJSON(groupedFrame, { format: "column" }) as GallicaGramRow[];
    rows = rows.map((row) => ({
      ...row,
      ratio: calculateRatio(row),
    }));
    return {
      data: rows.map((row) => [
        new Date(parseInt(row.annee), parseInt(row.mois) - 1).getTime(),
        row.ratio,
      ]),
      name: term,
    };
  } catch (error) {
    onNoRecordsFound();
    throw error;
  }
}

function calculateRatio(row: GallicaGramRow) {
  if (!row.total_sum) {
    return 0;
  }
  return row.n_sum / row.total_sum;
}
