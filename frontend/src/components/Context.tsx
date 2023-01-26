import React from "react";
import { trpc } from "../utils/trpc";

export const Context: React.FC<{
  url: string;
  term: string;
}> = ({ url, term }) => {
  const [pageIndex, setPageIndex] = React.useState(0);

  const arkCode = url.split("/").pop();
  if (!arkCode) {
    throw new Error("Ark code not defined");
  }

  const { data, isError } = trpc.context.useQuery({
    ark_code: arkCode,
    term,
  });

  if (!data) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return <div>Error</div>;
  }

  return (
    <div className={"flex w-full flex-col"}>
      <article
        className={
          "prose prose-lg m-auto p-5 text-justify lg:prose-lg xl:prose-2xl"
        }
        dangerouslySetInnerHTML={{ __html: data.pages[pageIndex].context }}
      />
      <div className={"grid justify-items-stretch pt-10"}>
        {pageIndex > 0 && (
          <button
            className={"justify-self-start"}
            onClick={() => setPageIndex(pageIndex - 1)}
          >
            Previous
          </button>
        )}
        <div className={"justify-self-center"}>
          Page {pageIndex + 1} of {data.num_results}
        </div>
        {pageIndex < data.num_results - 1 && (
          <button
            className={"justify-self-end"}
            onClick={() => setPageIndex(pageIndex + 1)}
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
};
