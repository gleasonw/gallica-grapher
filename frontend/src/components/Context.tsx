import React from "react";
import { GallicaRecord } from "../models/dbStructs";

export const Context: React.FC<{ record?: GallicaRecord }> = (props) => {
  const [pageIndex, setPageIndex] = React.useState(0);

  React.useEffect(() => {
    setPageIndex(0);
  }, [props.record]);
  
  console.log(pageIndex);

  const data = props.record?.context;

  if (!data || !data.pages || pageIndex >= data.pages.length) {
    return <div>Something broke :(</div>;
  }

  return (
    <div className={"flex w-full flex-col"}>
      <article
        className={"prose prose-lg m-auto h-60 text-justify lg:prose-lg"}
        dangerouslySetInnerHTML={{ __html: data.pages[pageIndex].context }}
      />
      <div className={"m-10 flex flex-row justify-between gap-10"}>
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
        {data.num_results > 0 && (
          <div className={"justify-center"}>
            {pageIndex + 1} of {data.num_results}
          </div>
        )}
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
