import React, { Suspense } from "react";
import { ImageSnippet } from "./ImageSnippet";
import { ContextQueryParams, fetchContext } from "./fetchContext";
import { ContextInputForm } from "../context/components/ContextInputForm";

export async function ImageTable({
  params,
}: {
  params: ContextQueryParams & { contextType?: "ocr" | "image" };
}) {
  const data = await fetchContext(params);

  return (
    <>
      <ContextInputForm
        params={params}
        num_results={parseInt(data?.num_results ?? "0")}
      />
      <div className={"flex flex-col gap-20 md:m-5"}>
        {data?.records?.map((record) => (
          <div
            key={record.ark}
            className={
              "md:border border-gray-400 md:shadow-lg md:rounded-lg md:p-10 flex flex-col gap-5 items-center"
            }
          >
            <h2 className={"text-lg"}>{record.paper_title}</h2>
            <h3>{record.author}</h3>
            <h4>{record.date}</h4>
            <Suspense
              fallback={
                <div
                  className={
                    "bg-gray-400 rounded h-80 w-full mb-4 animate-pulse border"
                  }
                />
              }
            >
              <ImageSnippet
                ark={record.ark}
                term={record.terms[0]}
                url={record.context?.[0]?.page_url}
              />
            </Suspense>
          </div>
        ))}
      </div>
    </>
  );
}
