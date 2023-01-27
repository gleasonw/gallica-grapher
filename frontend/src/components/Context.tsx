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
          "prose prose-lg m-auto p-5 text-justify lg:prose-lg"
        }
        dangerouslySetInnerHTML={{ __html: data.pages[pageIndex].context }}
      />
      <div className={"flex flex-row justify-between gap-10 m-10"}>
        {pageIndex > 0 ? (
          <button
            className={"text-3xl"}
            onClick={() => setPageIndex(pageIndex - 1)}
          >
            {"<"}
          </button>
        ) : (
          <div></div>
        )}
        <div className={"justify-center"}>
          {pageIndex + 1} of {data.num_results}
        </div>
        {pageIndex < data.num_results - 1 ? (
          <button
            className={"text-3xl"}
            onClick={() => setPageIndex(pageIndex + 1)}
          >
            {">"}
          </button>
        ) : (
          <div></div>
        )}
      </div>
    </div>
  );
};
