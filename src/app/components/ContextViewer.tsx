"use client";

import React from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "./design_system/button";
import { CardContent } from "./design_system/card";
import { imagePageKey } from "./utils";
import { Check, Copy, Image } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { components } from "@/src/app/types";
import { ImageSnippet } from "@/src/app/components/ImageSnippet";

export default function ContextViewer({
  record,
  isLoading,
}: {
  record: components["schemas"]["RowRecordResponse"]["records"][0];
  isLoading?: boolean;
}) {
  const [isPending, startTransition] = React.useTransition();
  const [hasCopied, setHasCopied] = React.useState(false);

  const [numShownPages, setNumShownPages] = React.useState(10);
  const pageNumbers = record.context?.map((page) => page.page_num);
  const uniqueFiltered = pageNumbers
    .filter((page, index) => pageNumbers.indexOf(page) === index)
    .sort((a, b) => {
      if (a === undefined || b === undefined) {
        return 0;
      }
      return a - b;
    });
  const ark = record.ark;

  const pathName = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const maybePageNumber = searchParams.get(`arkPage${ark}`);
  let pageNumber = record.context?.[0]?.page_num ?? 1;
  if (maybePageNumber && !isNaN(parseInt(maybePageNumber))) {
    pageNumber = parseInt(maybePageNumber);
  }
  const showImage = searchParams.get(imagePageKey(pageNumber, ark)) === "true";
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

  const referencePage =
    isPending || isLoading ? locallySelectedPage : pageNumber;

  return (
    <CardContent className={"flex flex-col gap-5 w-full"}>
      <div className={"flex gap-5"}>
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
        <div className="ml-auto flex gap-2">
          <Link
            href={`https://gallica.bnf.fr/ark:/12148/${ark}/f${pageNumber}.item`}
            target={"_blank"}
          >
            <Button variant="outline">Afficher sur Gallica</Button>
          </Link>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  onClick={() => {
                    navigator.clipboard.writeText(
                      `https://gallica.bnf.fr/ark:/12148/${ark}/f${pageNumber}.item`
                    );
                    setHasCopied(true);
                    setTimeout(() => setHasCopied(false), 2000);
                  }}
                >
                  {hasCopied ? <Check /> : <Copy />}
                </Button>
              </TooltipTrigger>
              <TooltipContent>Copier l'URL</TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <div
            className={`transition-all ${isPending && "opacity-50 transition-all"}`}
          >
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    onClick={() =>
                      appendKeyValAndPush(imagePageKey(pageNumber, ark), "true")
                    }
                    variant="outline"
                  >
                    <Image />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Afficher une image de la page</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </div>
      <div className={"flex flex-col gap-5 max-h-48 overflow-auto"}>
        {record.context
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

      {showImage && (
        <ImageSnippet
          ark={ark}
          term={record.terms[0]}
          pageNumber={pageNumber}
        />
      )}
    </CardContent>
  );
}
