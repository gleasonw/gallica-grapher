import React from "react";
import { ContextInputForm } from "./components/ContextInputForm";
import { fetchSRU } from "../components/fetchContext";
import { getSearchStateFromURL } from "../utils/searchState";
import { VolumeContext } from "../components/VolumeContext";

export default async function Page({
  searchParams,
}: {
  searchParams: Record<string, any>;
}) {
  const params = getSearchStateFromURL(searchParams);
  const contextParams = { ...params, terms: params?.terms ?? [] };
  const data = await fetchSRU(contextParams);

  const maybeNumberResults = data.total_records;
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
              <span className={"text-lg font-bold"}>{record.paper_title}</span>
              <span>{record.date}</span>
              <span>{record.author}</span>
            </h1>
            <VolumeContext
              ark={record.ark}
              term={record.terms[0]}
              pageNum={getArkImageFromParams(record.ark)}
              showImage={getImageStatusFromParams(record.ark)}
            />
          </div>
        ))}
      </div>
    </ContextInputForm>
  );
}
