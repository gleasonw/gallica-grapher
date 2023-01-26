import { ResultsTable } from "../../components/ResultsTable";
import { useRouter } from "next/router";

import { z } from "zod";

const tableSchema = z.object({
  terms: z.string(),
  year: z.coerce.number().nullish(),
  month: z.coerce.number().nullish(),
  day: z.coerce.number().nullish(),
});

export default function Context() {
  const router = useRouter();
  const params = router.query;

  const result = tableSchema.safeParse(params);

  if (!result.success) {
    console.log(result);
    return (
      <div>
        <p>Invalid query parameters</p>
        <div>{JSON.stringify(result.error, null, 4)}</div>
      </div>
    );
  } else {
    const { terms, year, month, day } = result.data;
    return (
      <ResultsTable
        terms={[terms]}
        year={year || 0}
        month={month || 0}
        day={day || 0}
      />
    );
  }
}
