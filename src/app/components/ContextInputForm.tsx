"use client";

import { useState } from "react";
import { Link1Icon } from "@radix-ui/react-icons";
import React from "react";
import { YearRangeInput } from "./YearRangeInput";
import InputBubble from "./InputBubble";
import { SelectInput } from "./SelectInput";
import { ContextQueryParams } from "./fetchContext";
import { QueryPagination } from "./QueryPagination";
import { Spinner } from "./Spinner";
import { useSubmit } from "./LoadingProvider";
import Link from "next/link";
import { Email } from "./email";

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
  params: ContextQueryParams;
  num_results: number;
  children: React.ReactNode;
};

export function ContextInputForm(props: ContextInputFormProps) {
  const [locallySelectedPage, setLocallySelectedPage] = React.useState<
    number | null
  >(null);
  const [contextForm, setContextParams] = useState<ContextQueryParams>(
    props.params
  );

  const translation = strings.fr;

  const { handleSubmit, isPending } = useSubmit();

  const params = props.params;

  const currentPage = Math.floor((params.cursor ?? 0) / 10) + 1;

  const totalPages = Math.floor((props.num_results ?? 0) / 10);

  function setNewPage(newPage: number) {
    setLocallySelectedPage(newPage);
    handleSubmit({ cursor: (newPage - 1) * 10 });
  }

  function handleUpdateParams<T extends keyof ContextQueryParams>(
    key: T,
    value: ContextQueryParams[T]
  ) {
    setContextParams({
      ...contextForm,
      [key]: value,
    });
  }

  const referencePage = isPending ? locallySelectedPage : currentPage;

  return (
    <>
      <form
        className={
          "w-full flex flex-col justify-center gap-10 items-center rounded-lg pt-5 pb-5"
        }
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit(contextForm);
        }}
      >
        <InputBubble
          word={contextForm.terms?.[0] ?? ""}
          onWordChange={(word) => handleUpdateParams("terms", [word])}
        >
          <button className="bg-blue-700 text-sm pl-5 pr-5 hover:bg-blue-500 text-white absolute top-4 right-5 rounded-full p-3 shadow-md">
            {isPending ? <Spinner isFetching /> : "Explore"}
          </button>
        </InputBubble>
        <div className={"flex flex-wrap gap-10 justify-center"}>
          <YearRangeInput
            min={1500}
            max={2023}
            value={[contextForm.year ?? 1789, contextForm.end_year ?? 1950]}
            showLabel={true}
            onChange={(value) => {
              setContextParams({
                ...contextForm,
                year: value ? value[0] : contextForm.year,
                end_year: value ? value[1] : contextForm.end_year,
                cursor: 0,
              });
            }}
          />
          <SelectInput
            label={"corpus"}
            options={["all", "book", "periodical"] as const}
            value={contextForm.source}
            onChange={(new_source) => {
              handleUpdateParams("source", new_source);
            }}
          />
          <SelectInput
            label={"sort"}
            value={contextForm.sort}
            options={["date", "relevance"] as const}
            onChange={(sort) =>
              setContextParams({
                ...contextForm,
                sort: sort,
              })
            }
          />
          <SelectInput
            label={"limit"}
            value={contextForm.limit ?? 10}
            options={[10, 20, 50]}
            onChange={(limit) => handleUpdateParams("limit", limit)}
          />
        </div>
        <div className="flex flex-wrap gap-5 items-center">
          <input
            type="text"
            value={contextForm.link_term || ""}
            onChange={(e) =>
              handleUpdateParams("link_term", e.target.value || undefined)
            }
            className={"border p-2 rounded-lg shadow-sm"}
            placeholder={translation.linkTerm}
          />
          <Link1Icon className="w-6 h-6" />
          <input
            type="number"
            value={contextForm.link_distance ?? ""}
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
      </form>
      <QueryPagination
        cursorMax={totalPages}
        selectedPage={referencePage ?? 1}
        onChange={setNewPage}
      />
      <div className={`transition-all ${isPending && "opacity-50"}`}>
        {props.children}
      </div>
    </>
  );
}
