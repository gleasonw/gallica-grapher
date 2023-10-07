"use client";

import React from "react";
import { RowRecordResponse } from "./fetchContext";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { GallicaButton } from "./design_system/GallicaButton";
import Link from "next/link";

export default function ContextViewer({
  data,
  children,
  ark,
  isLoading,
}: {
  data: RowRecordResponse["records"][0]["context"];
  children: React.ReactNode;
  ark: string;
  isLoading?: boolean;
}) {
  const [isPending, startTransition] = React.useTransition();

  const [numShownPages, setNumShownPages] = React.useState(10);
  const pageNumbers = data?.map((page) => page.page_num);
  const uniqueFiltered = pageNumbers
    .filter((page, index) => pageNumbers.indexOf(page) === index)
    .sort((a, b) => {
      if (a === undefined || b === undefined) {
        return 0;
      }
      return a - b;
    });

  const pathName = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const maybePageNumber = searchParams.get(`arkPage${ark}`);
  let pageNumber = data?.[0]?.page_num ?? 1;
  if (maybePageNumber && !isNaN(parseInt(maybePageNumber))) {
    pageNumber = parseInt(maybePageNumber);
  }
  const showImage = searchParams.get(`${ark}-withImage`) === "true";
  const [locallySelectedPage, setLocallySelectedPage] = React.useState<
    number | undefined
  >(pageNumber);

  function handleSetPageNumber(newPageNumber: number | undefined) {
    if (newPageNumber === null) {
      return;
    }
    setLocallySelectedPage(newPageNumber);
    if (newPageNumber) {
      return appendKeyValAndPush(`arkPage${ark}`, newPageNumber.toString());
    }
  }

  function appendKeyValAndPush(key: string, val: string) {
    const searchParamsCopy = new URLSearchParams(searchParams.toString());
    searchParamsCopy.set(key, val);
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
            Afficher 10 pages supplémentaires (sur{" "}
            {uniqueFiltered?.length - numShownPages})
          </GallicaButton>
        )}
      </div>
      <div className={"flex flex-col gap-5"}>
        {data
          ?.filter((page) => page.page_num === referencePage)
          .map((page, index) => (
            <span
              key={`${page.left_context}${page.page_num}${page.right_context}${index}`}
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
      <div
        className={`transition-all ${
          (isPending || isLoading) && "opacity-50 transition-all"
        }`}
      >
        {children}
        {!showImage && (
          <GallicaButton
            onClick={() => appendKeyValAndPush(`${ark}-withImage`, "true")}
          >
            {"Afficher une image de la page "}
          </GallicaButton>
        )}
      </div>
      <Link
        href={`https://gallica.bnf.fr/ark:/12148/${ark}/f${pageNumber}.item`}
        className={"underline text-blue-500"}
        target={"_blank"}
      >
        Afficher sur Gallica
      </Link>
    </div>
  );
}
