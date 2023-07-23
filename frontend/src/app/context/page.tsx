import React, { Suspense } from "react";
import { z } from "zod";
import { OCRTable } from "../components/OCRTable";
import { ImageTable } from "../components/ImageTable";

const searchPageState = z.object({
  terms: z.string().optional(),
  year: z.coerce.number().optional(),
  end_year: z.coerce.number().optional(),
  month: z.coerce.number().optional(),
  day: z.coerce.number().optional(),
  source: z
    .literal("book")
    .or(z.literal("periodical"))
    .or(z.literal("all"))
    .optional(),
  link_term: z.string().optional(),
  link_distance: z.coerce.number().optional(),
  codes: z.string().array().optional(),
  limit: z.coerce.number().optional(),
  sort: z.literal("date").or(z.literal("relevance")).optional(),
  cursor: z.number().optional(),
  contextType: z.literal("ocr").or(z.literal("image")).optional(),
});

export default async function Page({ searchParams }: { searchParams: any }) {
  const result = searchPageState.safeParse(searchParams);
  if (!result.success) {
    return <div>Invalid search params: {result.error.message}</div>;
  }

  const loadingSkeleton = (
    <div className={"flex flex-col gap-20 md:m-5"}>
      {[...Array(10)].map((_, i) => (
        <div
          key={i}
          className={
            "animate-pulse md:border border-gray-400 md:shadow-lg md:rounded-lg md:p-10 flex flex-col gap-5 items-center"
          }
        >
          <div className={"text-lg bg-gray-400 rounded h-6 w-3/4 mb-4"}></div>
          <div className={"bg-gray-400 rounded h-4 w-1/2 mb-4"}></div>
          <div className={"bg-gray-400 rounded h-4 w-1/4 mb-4"}></div>
          <div className={"bg-gray-400 rounded h-80 w-full mb-4"}></div>
        </div>
      ))}
    </div>
  );

  const params = result.data;
  const contextParams = { ...params, terms: params.terms ?? "choucroute" };

  if (!params.contextType || params.contextType === "image") {
    return (
      <Suspense fallback={loadingSkeleton}>
        <ImageTable params={contextParams} />
      </Suspense>
    );
  } else {
    return (
      <Suspense fallback={<div>Loading...</div>}>
        <OCRTable params={contextParams} />
      </Suspense>
    );
  }
}
