"use client";

import { useState } from "react";
import { Link1Icon } from "@radix-ui/react-icons";
import React from "react";
import { YearRangeInput } from "../../components/YearRangeInput";
import InputBubble from "../../components/InputBubble";
import { SelectInput } from "../../components/SelectInput";
import { useRouter } from "next/navigation";
import { addQueryParamsIfExist } from "../../utils/addQueryParamsIfExist";
import { ContextQueryParams } from "../../components/fetchContext";
import { ToggleOptions } from "../../components/ToggleOptions";
import { QueryPagination } from "../../components/QueryPagination";
import { ContextLoadingSkeleton } from "../page";

export const strings = {
  fr: {
    title: "The Gallica Grapher",
    description:
      "Explorez les occurrences de mots dans des périodiques Gallica.",
    linkTerm: "Terme de proximité",
    linkDistance: "Distance de proximité",
  },
  en: {
    title: "The Gallica Grapher",
    description: "Explore word occurrences in archived Gallica periodicals.",
    linkTerm: "Link term",
    linkDistance: "Link distance",
  },
};

export type ContextInputFormProps = {
  params: ContextQueryParams & { contextType?: "image" | "ocr" };
  num_results: number;
  children: React.ReactNode;
};

type FormState = Partial<ContextQueryParams & { contextType: "image" | "ocr" }>;

export function ContextInputForm(props: ContextInputFormProps) {
  const [contextParams, setContextParams] = useState<FormState>(props.params);
  const [isPending, startTransition] = React.useTransition();

  const translation = strings.fr;

  const router = useRouter();

  function handleSubmit() {
    const url = addQueryParamsIfExist("/context", contextParams);
    startTransition(() => router.push(url));
  }

  const params = props.params;

  const currentPage = Math.ceil((params.cursor ?? 0) / (params.limit ?? 10));

  const totalPages = Math.ceil((props.num_results ?? 0) / (params.limit ?? 10));

  function setNewPage(newPage: number) {
    setContextParams({
      ...contextParams,
      cursor: (newPage - 1) * (params.limit ?? 10),
    });
  }

  function handleUpdateParams<T extends keyof FormState>(
    key: T,
    value: FormState[T]
  ) {
    setContextParams({
      ...contextParams,
      [key]: value,
    });
  }

  return (
    <>
      <div
        className={
          "w-full flex flex-col justify-center gap-10 items-center rounded-lg pt-5 pb-5"
        }
      >
        <InputBubble
          word={contextParams.terms ?? ""}
          onWordChange={(word) => handleUpdateParams("terms", word)}
          onSubmit={handleSubmit}
        >
          <button
            onSubmit={handleSubmit}
            className="bg-blue-700 text-sm pl-5 pr-5 hover:bg-blue-500 text-white absolute top-4 right-5 rounded-full p-3 shadow-md"
          >
            Explore
          </button>
        </InputBubble>
        <div className={"flex flex-wrap gap-10 justify-center"}>
          <YearRangeInput
            min={1500}
            max={2023}
            value={[contextParams.year, contextParams.end_year]}
            showLabel={true}
            onChange={(value) => {
              setContextParams({
                ...contextParams,
                year: value ? value[0] : contextParams.year,
                end_year: value ? value[1] : contextParams.end_year,
              });
            }}
          />
          <SelectInput
            label={"corpus"}
            options={["book", "periodical", "all"] as const}
            value={contextParams.source}
            onChange={(new_source) => {
              handleUpdateParams("source", new_source);
            }}
          />
          <SelectInput
            label={"sort"}
            value={contextParams.sort}
            options={["date", "relevance"] as const}
            onChange={(sort) =>
              setContextParams({
                ...contextParams,
                sort: sort,
              })
            }
          />
          <SelectInput
            label={"limit"}
            value={contextParams.limit}
            options={[10, 20, 50]}
            onChange={(limit) => handleUpdateParams("limit", limit)}
          />
        </div>
        <div className="flex flex-wrap gap-5 items-center">
          <input
            type="text"
            value={contextParams.link_term || ""}
            onChange={(e) =>
              handleUpdateParams("link_term", e.target.value || undefined)
            }
            className={"border p-2 rounded-lg shadow-sm"}
            placeholder={translation.linkTerm}
          />
          <Link1Icon className="w-6 h-6" />
          <input
            type="number"
            value={contextParams.link_distance}
            onChange={(e) => {
              const numVal = parseInt(e.target.value);
              if (typeof numVal === "number" && !isNaN(numVal) && numVal >= 0) {
                handleUpdateParams("link_distance", numVal);
              } else if (e.target.value === "") {
                handleUpdateParams("link_distance", undefined);
              }
            }}
            className={"border p-2 rounded-lg shadow-sm"}
            placeholder={translation.linkDistance}
          />
        </div>

        <QueryPagination
          cursorMax={totalPages}
          selectedPage={currentPage}
          onChange={setNewPage}
        />
      </div>
      {
        // a suspense workaround since next router.push() is buggy and doesn't navigate immediately
        isPending ? <ContextLoadingSkeleton /> : props.children
      }
    </>
  );
}
