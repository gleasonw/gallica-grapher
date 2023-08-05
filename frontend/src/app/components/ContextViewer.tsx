"use client";

import React from "react";
import { fetchVolumeContext } from "./fetchContext";

export default function ContextViewer({
  data,
  children,
}: {
  data: Awaited<ReturnType<typeof fetchVolumeContext>>;
  children: React.ReactNode;
}) {
  const [pageNumber, setPageNumber] = React.useState(1);

  const pageNumbers = data?.map((page) => page.page_num);
  const uniqueFiltered = pageNumbers
    .filter((page, index) => pageNumbers.indexOf(page) === index)
    .sort((a, b) => a - b);

  return (
    <div>
      <div className={"flex flex-wrap gap-10"}>
        {uniqueFiltered?.map((pageNumber) => (
          <span key={pageNumber} onClick={() => setPageNumber(pageNumber)}>
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
