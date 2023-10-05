import React from "react";
import { ContextInputForm } from "../components/ContextInputForm";
import { fetchContext, fetchSRU } from "../components/fetchContext";
import { getSearchStateFromURL } from "../utils/searchState";
import { LoadingProvider } from "../components/LoadingProvider";
import ContextViewer from "../components/ContextViewer";
import { ImageSnippet } from "../components/ImageSnippet";

export default async function Page({
  searchParams,
}: {
  searchParams: Record<string, any>;
}) {
  const params = getSearchStateFromURL(searchParams);
  const contextParams = {
    ...params,
    terms: params?.terms ?? [],
    all_context: true,
  };
  console.log({ params });
  const data = params.terms?.some((term) => !!term)
    ? await fetchContext(contextParams)
    : { records: [], num_results: 0 };

  const maybeNumberResults = data.num_results;
  let numResults = 0;
  if (!isNaN(maybeNumberResults) && maybeNumberResults > 0) {
    numResults = maybeNumberResults;
  }

  function getArkImageFromParams(ark: string) {
    if (Object.keys(searchParams)?.includes(`arkPage${ark}`)) {
      return searchParams[`arkPage${ark}`];
    }
  }

  function getImageStatusFromParams(ark: string) {
    if (Object.keys(searchParams)?.includes(`${ark}-withImage`)) {
      return searchParams[`${ark}-withImage`] === "true";
    }
  }

  return (
    <LoadingProvider>
      <ContextInputForm params={contextParams} num_results={numResults}>
        <div className={"flex flex-col gap-20 md:m-5"}>
          {data.records?.map((record, index) => (
            <div
              key={`${record.ark}-${record.terms}-${index}`}
              className={
                "border-gray-400 border md:shadow-lg md:rounded-lg md:p-10 flex flex-col gap-5  w-full"
              }
            >
              <h1 className={"flex flex-col gap-5 flex-wrap"}>
                <span className={"text-lg font-bold"}>
                  {record.paper_title}
                </span>
                <span>{record.date}</span>
                <span>{record.author}</span>
              </h1>
              <ContextViewer data={record.context} ark={record.ark}>
                {getImageStatusFromParams(record.ark) && (
                  <ImageSnippet
                    ark={record.ark}
                    term={record.terms[0]}
                    pageNumber={
                      getArkImageFromParams(record.ark) ??
                      record.context[0].page_num
                    }
                  />
                )}
              </ContextViewer>
            </div>
          ))}
        </div>
      </ContextInputForm>
    </LoadingProvider>
  );
}
