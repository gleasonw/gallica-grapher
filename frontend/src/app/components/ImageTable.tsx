import React, { Suspense } from "react";
import { ImageSnippet } from "./ImageSnippet";
import { ContextQueryParams, fetchContext } from "./fetchContext";

export async function ImageTable({
  params,
}: {
  params: ContextQueryParams & { contextType?: "ocr" | "image" };
}) {
  const data = await fetchContext(params);

  return (
    <>
      <div className={"flex flex-col gap-20 md:m-5 "}>
        {data?.records?.map((record) => (
          <div
            key={record.ark}
            className={
              "md:border border-gray-400 md:shadow-lg md:rounded-lg md:p-10 flex flex-row gap-5 items-center flex-wrap"
            }
          >
            <div
              className={
                "flex flex-col justify-center items-center w-full relative"
              }
            >
              <h2 className={"text-xl pb-5"}>{record.paper_title}</h2>
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
            <div className={"flex flex-col gap-10 max-h-full overflow-auto"}>
              {record.context?.map((context) => (
                <a
                  key={context.page_url}
                  href={context.page_url}
                  target={"_blank"}
                  rel={"noreferrer"}
                >
                  <span>{context.left_context}</span>
                  <span className={"bg-yellow-200"}>{context.pivot}</span>
                  <span>{context.right_context}</span>
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
