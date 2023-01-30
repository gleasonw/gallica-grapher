import { ResultsTable } from "../../components/ResultsTable";
import { useRouter } from "next/router";
import { z } from "zod";
import { tableParamSchema } from "../../models/tableParamSchema";


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
    return (
      <ResultsTable
        terms={terms}
        year={year}
        month={month}
        day={day}
        source={source}
        codes={codes || []}
        limit={20}
        link_term={link_term}
        link_distance={link_distance}
        sort={sort}
      />
    );
  }
}
