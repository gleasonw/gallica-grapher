import React from "react";
import { trpc } from "../utils/trpc";


export const Context: React.FC<{
  url: string;
  term: string;
  onHideContextClick: () => void;
}> = ({ url, term, onHideContextClick }) => {
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
    <td className={"w-full flex flex-col"}>
      <button
        onClick={onHideContextClick}
        className={"p-5 text-3xl flex flex-row-reverse"}
      >
        X
      </button>
      <div
        className={"prose m-auto overflow-scroll"}
        dangerouslySetInnerHTML={{ __html: data.pages[pageIndex].context }} />
      <div className={"grid justify-items-stretch pt-10"}>
        {pageIndex > 0 && (
          <button
            className={"justify-self-start"}
            onClick={() => setPageIndex(pageIndex - 1)}
          >
            Previous
          </button>
        )}
        <div className={'justify-self-center'}>
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
    </td>
  );
};
