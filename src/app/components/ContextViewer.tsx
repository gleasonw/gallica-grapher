"use client";

import React from "react";
import { RowRecordResponse } from "./fetchContext";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { GallicaButton } from "./design_system/GallicaButton";
import Link from "next/link";
import { Button } from "./design_system/button";
import { CardContent } from "./design_system/card";

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
    <CardContent className={"flex flex-col gap-5 w-full"}>
      <div className={"flex flex-wrap gap-10"}>
        {uniqueFiltered?.slice(0, numShownPages).map((currentPage) => (
          <Button
            variant="outline"
            key={currentPage}
            onClick={() => handleSetPageNumber(currentPage)}
            className={
              currentPage === referencePage ? "bg-gray-200" : "bg-white"
            }
          >
            {currentPage}
          </Button>
        ))}
        {numShownPages < uniqueFiltered?.length && (
          <Button
            variant="outline"
            onClick={() => setNumShownPages(numShownPages + 10)}
          >
            Afficher 10 pages supplémentaires (sur{" "}
            {uniqueFiltered?.length - numShownPages})
          </Button>
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
              <span className={" font-bold px-8"}>{page.pivot}</span>{" "}
              {page.right_context}
            </span>
          ))}
      </div>
      {children}
      <div className="flex gap-4">
        <div
          className={`transition-all ${
            (isPending || isLoading) && "opacity-50 transition-all"
          }`}
        >
          {!showImage && (
            <Button
              onClick={() => appendKeyValAndPush(`${ark}-withImage`, "true")}
              variant="outline"
            >
              Afficher une image de la page
            </Button>
          )}
        </div>
        <Link
          href={`https://gallica.bnf.fr/ark:/12148/${ark}/f${pageNumber}.item`}
          target={"_blank"}
        >
          <Button variant="outline">Afficher sur Gallica</Button>
        </Link>
      </div>
    </CardContent>
  );
}
