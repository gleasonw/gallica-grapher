"use client";

import React from "react";
import { fetchVolumeContext } from "./fetchContext";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

export default function ContextViewer({
  data,
  children,
  ark,
}: {
  data: Awaited<ReturnType<typeof fetchVolumeContext>>;
  children: React.ReactNode;
  ark: string;
}) {
  const pageNumbers = data?.map((page) => page.page_num);
  const uniqueFiltered = pageNumbers
    .filter((page, index) => pageNumbers.indexOf(page) === index)
    .sort((a, b) => a - b);

  const pathName = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const maybePageNumber = searchParams.get(`${ark}%page`);
  let pageNumber = 1;
  if (maybePageNumber && !isNaN(parseInt(maybePageNumber))) {
    pageNumber = parseInt(maybePageNumber);
  }

  function handleSetPageNumber(newPageNumber: number) {
    const searchParamsCopy = new URLSearchParams(searchParams.toString());
    searchParamsCopy.set(`arkPage${ark}`, newPageNumber.toString());
    return router.push(pathName + "?" + searchParamsCopy, { scroll: false });
  }

  return (
    <div>
      <div className={"flex flex-wrap gap-10"}>
        {uniqueFiltered?.map((pageNumber) => (
          <span
            key={pageNumber}
            onClick={() => handleSetPageNumber(pageNumber)}
          >
            {pageNumber}
          </span>
        ))}
      </div>
      <div className={"flex flex-col gap-5"}>
        {data
          ?.filter((page) => page.page_num === pageNumber)
          .map((page) => (
            <span
              key={`${page.left_context}${page.page_num}${page.right_context}`}
            >
              {page.left_context}{" "}
              <span className={"text-blue-500 font-medium pl-5 pr-5"}>
                {page.pivot}
              </span>{" "}
              {page.right_context}
            </span>
          ))}
      </div>
      {children}
    </div>
  );
}
