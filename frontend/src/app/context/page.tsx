import React from "react";
import { z } from "zod";
import { SearchableContext } from "./components/SearchableContext";

const searchPageState = z.object({
  terms: z.string().optional(),
  year: z.coerce.number().optional(),
  end_year: z.coerce.number().optional(),
  month: z.coerce.number().optional(),
  day: z.coerce.number().optional(),
  source: z
    .literal("book")
    .or(z.literal("periodical"))
    .or(z.literal("all"))
    .optional(),
  link_term: z.string().optional(),
  link_distance: z.coerce.number().optional(),
  codes: z.string().array().optional(),
  limit: z.coerce.number().optional(),
  sort: z.literal("date").or(z.literal("relevance")).optional(),
  cursor: z.number().optional(),
});

export default function Page({ searchParams }: { searchParams: any }) {
  const result = searchPageState.safeParse(searchParams);
  if (!result.success) {
    return <div>Invalid search params: {result.error.message}</div>;
  }
  return <SearchableContext initParams={result.data} />;
}
