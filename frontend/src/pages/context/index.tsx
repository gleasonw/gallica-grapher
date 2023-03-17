import { ResultsTable } from "../../components/ResultsTable";
import { useRouter } from "next/router";
import { z } from "zod";

const tableParamSchema = z.object({
  terms: z.string(),
  year: z.coerce.number().nullish(),
  month: z.coerce.number().nullish(),
  day: z.coerce.number().nullish(),
  source: z
    .literal("book")
    .or(z.literal("periodical"))
    .or(z.literal("all"))
    .nullish(),
  link_term: z.string().nullish(),
  link_distance: z.coerce.number().nullish(),
  codes: z.string().array().nullish(),
  limit: z.coerce.number().nullish(),
  sort: z.literal("date").or(z.literal("relevance")).nullish(),
  cursor: z.number().nullish(),
});

export default function Context() {
  const router = useRouter();
  const params = router.query;

  const result = tableParamSchema.safeParse(params);

  if (!result.success) {
    console.log(result);
    return (
      <p>
        Invalid query parameters (could be misspelling, missing value, etc...)
        -- check console for detailed error
      </p>
    );
  } else {
    const {
      terms,
      year,
      month,
      day,
      source,
      codes,
      link_distance,
      link_term,
      limit,
      sort,
    } = result.data;
    if (limit && limit > 50) {
      return (
        <p>
          Limit must be less than or equal to 50, the maximum number of records
          Gallica returns in one request
        </p>
      );
    }
    if (
      (link_distance && link_term === undefined) ||
      (link_term && link_distance === undefined)
    ) {
      return (
        <p>
          If you specify a link_term, you must also specify a link_distance, and
          vice versa
        </p>
      );
    }
    const splitTerms = terms.split(" ");

    return (
      <ResultsTable
        terms={splitTerms}
        yearRange={[year || undefined, undefined]}
        month={month}
        day={day}
        source={source}
        codes={codes || []}
        link_term={link_term}
        limit={10}
        link_distance={link_distance}
        sort={sort}
      />
    );
  }
}
