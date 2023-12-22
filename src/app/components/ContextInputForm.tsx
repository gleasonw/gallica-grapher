"use client";

import { useState } from "react";
import React from "react";
import { ContextQueryParams } from "./fetchContext";
import { useSubmit } from "./LoadingProvider";
import { SelectBase } from "./select";
import { SelectItem, SelectValue } from "./design_system/select";
import { Input } from "./design_system/input";
import { Button } from "./design_system/button";
import { Label } from "./design_system/label";
import { NumberInput } from "./number-input";

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
    <div className="flex flex-col items-center mt-6 gap-6">
      <form
        className={"flex flex-col gap-6 mb-6 max-w-3xl"}
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit(contextForm);
        }}
      >
        <section className="flex gap-4 items-center">
          <Input
            id="search"
            className="text-3xl p-5 py-10 shadow-md"
            placeholder="Search for a term"
            value={contextForm.terms[0]}
            onChange={(e) => handleUpdateParams("terms", [e.target.value])}
          />
        </section>

        <section className="flex gap-4 items-center">
          <div className="flex gap-2 flex-col">
            <Label htmlFor="year">Year</Label>
            <NumberInput
              value={contextForm.year ?? 1789}
              onValueChange={(year) => handleUpdateParams("year", year)}
              className="flex-1"
              id="year"
              placeholder="YYYY"
              type="number"
            />
          </div>

          <div className="flex gap-2 flex-col">
            <Label htmlFor="end_year">End Year</Label>
            <NumberInput
              value={contextForm.end_year ?? 1950}
              onValueChange={(year) => handleUpdateParams("end_year", year)}
              className="flex-1"
              id="end_year"
              type="number"
              placeholder="YYYY"
            />
          </div>

          <SelectBase
            label="Source"
            value={contextForm.source}
            onChange={(value) => handleUpdateParams("source", value as any)}
            trigger={<SelectValue placeholder="All" />}
          >
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="newspapers">Newspapers</SelectItem>
            <SelectItem value="magazines">Magazines</SelectItem>
          </SelectBase>

          <SelectBase
            label="Sort"
            value={contextForm.sort}
            onChange={(value) => handleUpdateParams("sort", value as any)}
            trigger={<SelectValue placeholder="Date" />}
          >
            <SelectItem value="date">Date</SelectItem>
            <SelectItem value="relevance">Relevance</SelectItem>
          </SelectBase>

          <SelectBase
            label="Limit"
            trigger={<SelectValue placeholder="10" />}
            value={contextForm.limit?.toString()}
            onChange={(value) => handleUpdateParams("limit", parseInt(value))}
          >
            <SelectItem value="10">10</SelectItem>
            <SelectItem value="20">20</SelectItem>
            <SelectItem value="50">50</SelectItem>
          </SelectBase>
        </section>
        <Button className="whitespace-nowrap">Explore</Button>
      </form>
      <div className={`transition-all ${isPending && "opacity-50"}`}>
        {props.children}
      </div>
    </div>
  );
}
