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
  link: z.tuple([z.string(), z.number()]).nullish(),
  codes: z.string().array().nullish(),
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
    const { terms, year, month, day, source, codes, link } = result.data;
    return (
      <ResultsTable
        terms={[terms]}
        year={year || 0}
        month={month || 0}
        day={day || 0}
        source={source || "all"}
        codes={codes || []}
        link={link}
      />
    );
  }
}
