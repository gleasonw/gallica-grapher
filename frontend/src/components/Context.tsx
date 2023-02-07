import React from "react";
import { GallicaRecord } from "../models/dbStructs";

export const Context: React.FC<{ record?: GallicaRecord }> = (props) => {
  const [pageIndex, setPageIndex] = React.useState(0);

  React.useEffect(() => {
    setPageIndex(0);
  }, [props.record]);

  const data = props.record?.context;

  if (!data || !data.pages || pageIndex >= data.pages.length) {
    return <div>Something broke </div>;
  }

  const handleLeftPageTurn = () => {
    if (pageIndex > 0) {
      setPageIndex(pageIndex - 1);
    }
  };

  const handleRightPageTurn = () => {
    if (pageIndex < data.pages.length - 1) {
      setPageIndex(pageIndex + 1);
    }
  };

  return (
    <div className={"relative flex w-full flex-col"}>
      {data.pages && data.pages.length > 1 && (
        <div className={" absolute flex h-full w-full flex-row"}>
          <button
            onClick={() => handleLeftPageTurn()}
            className={"h-full w-full"}
          />
          <button
            onClick={() => handleRightPageTurn()}
            className={"h-full w-full"}
          />
        </div>
      )}
      <article
        className={"min-h-60 prose prose-lg m-auto text-justify lg:prose-lg z-10"}
        dangerouslySetInnerHTML={{ __html: data.pages[pageIndex].context }}
      />
      <div className={"m-10 flex flex-row justify-center text-xl"}>
        {data.num_results > 0 && (
          <div className={"flex flex-row gap-20"}>
            {pageIndex > 0 ? <p>{"<"}</p> : <p></p>}
            <div className={"justify-center"}>
              {pageIndex + 1} of {data.num_results}
            </div>
            {pageIndex < data.pages.length - 1 ? <p>{">"}</p> : <p></p>}
          </div>
        )}
      </div>
    </div>
  );
};
