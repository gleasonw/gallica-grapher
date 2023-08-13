"use client";

import React from "react";
import { fetchVolumeContext } from "./fetchContext";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { GallicaButton } from "../design_system/GallicaButton";

export default function ContextViewer({
  data,
  children,
  ark,
}: {
  data: Awaited<ReturnType<typeof fetchVolumeContext>>;
  children: React.ReactNode;
  ark: string;
}) {
  const [isPending, startTransition] = React.useTransition();
  const [locallySelectedPage, setLocallySelectedPage] = React.useState<
    number | null
  >(null);
  const [numShownPages, setNumShownPages] = React.useState(10);
  const pageNumbers = data?.map((page) => page.page_num);
  const uniqueFiltered = pageNumbers
    .filter((page, index) => pageNumbers.indexOf(page) === index)
    .sort((a, b) => a - b);

  const pathName = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const maybePageNumber = searchParams.get(`arkPage${ark}`);
  let pageNumber = data?.[0]?.page_num ?? 1;
  if (maybePageNumber && !isNaN(parseInt(maybePageNumber))) {
    pageNumber = parseInt(maybePageNumber);
  }

  function handleSetPageNumber(newPageNumber: number) {
    setLocallySelectedPage(newPageNumber);
    const searchParamsCopy = new URLSearchParams(searchParams.toString());
    searchParamsCopy.set(`arkPage${ark}`, newPageNumber.toString());
    return startTransition(() =>
      router.push(pathName + "?" + searchParamsCopy, { scroll: false })
    );
  }

  const referencePage = isPending ? locallySelectedPage : pageNumber;

  return (
    <div className={"flex flex-col gap-5 w-full"}>
      <div className={"flex flex-wrap gap-10"}>
        {uniqueFiltered?.slice(0, numShownPages).map((currentPage) => (
          <GallicaButton
            key={currentPage}
            onClick={() => handleSetPageNumber(currentPage)}
            className={
              currentPage === referencePage ? "bg-gray-200" : "bg-white"
            }
          >
            {currentPage}
          </GallicaButton>
        ))}
        {numShownPages < uniqueFiltered?.length && (
          <GallicaButton onClick={() => setNumShownPages(numShownPages + 10)}>
            Show 10 more (out of {uniqueFiltered?.length - numShownPages})
          </GallicaButton>
        )}
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
      <div className={"w-full border"} />
      {isPending ? (
        <div className={"bg-gray-400 rounded h-80 w-full mb-4"} />
      ) : (
        children
      )}
    </div>
  );
}
