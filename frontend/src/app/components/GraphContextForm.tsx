"use client";

import React from "react";
import { useSearchState } from "../composables/useSearchState";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { SelectInput } from "./SelectInput";
import { useRouter } from "next/navigation";
import { QueryPagination } from "./QueryPagination";
import { SearchState } from "../utils/searchState";

const gallica_plug = (
  <a
    href="https://shiny.ens-paris-saclay.fr/app/gallicagram"
    target="_blank"
    rel="noreferrer"
    className="text-blue-500 underline"
  >
    Gallicagram
  </a>
);

const strings = {
  fr: {
    title: "The Gallica Grapher",
    description:
      "Explorez les occurrences de mots dans des périodiques Gallica.",
    linkTerm: "Terme de proximité",
    linkDistance: "Distance de proximité",
    zoom_out: "Zoomer à l'échelle originale",
    gallicagram_plug: (
      <>
        <p>
          Données de charte fournies par {gallica_plug}, un projet de Benjamin
          Azoulay et Benoît de Courson.
        </p>
      </>
    ),
    grouping: "Résolution",
    smoothing: "Lissage",
    months: [
      "Janvier",
      "Février",
      "Mars",
      "Avril",
      "Mai",
      "Juin",
      "Juillet",
      "Août",
      "Septembre",
      "Octobre",
      "Novembre",
      "Décembre",
    ],
  },
  en: {
    title: "The Gallica Grapher",
    description: "Explore word occurrences in archived Gallica periodicals.",
    linkTerm: "Link term",
    linkDistance: "Link distance",
    zoom_out: "Zoom out",
    gallicagram_plug: (
      <>
        <p>
          Chart data provided by {gallica_plug}, a project by Benjamin Azoulay
          and Benoît de Courson.
        </p>
      </>
    ),
    grouping: "Grouping",
    smoothing: "Smoothing",
    months: [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ],
  },
};

export default function GraphContextForm({
  numResults,
  children,
}: {
  numResults?: number;
  children?: React.ReactNode;
}) {
  const [isPending, startTransition] = React.useTransition();
  const [locallySelectedPage, setLocallySelectedPage] =
    React.useState<number>(1);
  const translation = strings["fr"];
  const searchState = useSearchState();
  const { terms, selected_term, year, end_year, month, cursor } = searchState;
  const router = useRouter();

  const currentPage = Math.floor((cursor ?? 0) / 10) + 1;

  const totalPages = Math.floor((numResults ?? 0) / 10);

  function handleSubmit(params: SearchState) {
    const url = addQueryParamsIfExist("/", {
      ...searchState,
      ...params,
    });
    startTransition(() => router.push(url, { scroll: false }));
  }

  function setNewPage(newPage: number) {
    setLocallySelectedPage(newPage);
    handleSubmit({
      cursor: (newPage - 1) * 10,
    });
  }

  const referencePage = isPending ? locallySelectedPage : currentPage;

  return (
    <>
      <div className={"flex flex-col gap-5 ml-5 mr-5 mt-2"}>
        {translation.gallicagram_plug}
        <div className={"flex wrap gap-10"}>
          <SelectInput
            options={terms?.map((term) => term) ?? []}
            onChange={(value: string) => handleSubmit({ selected_term: value })}
            value={terms?.find((t) => t === selected_term)}
          />
          <ContextFilter
            onClick={() =>
              handleSubmit({ year: undefined, end_year: undefined })
            }
            label={year && end_year ? `${year} - ${end_year}` : undefined}
          />
          <ContextFilter
            label={month ? translation.months[month - 1] : undefined}
            onClick={() => handleSubmit({ month: undefined })}
          />
        </div>
      </div>
      <QueryPagination
        cursorMax={totalPages}
        selectedPage={referencePage ?? 1}
        onChange={setNewPage}
      />
      {children}
    </>
  );
}

function ContextFilter({
  label,
  onClick,
}: {
  label: any;
  onClick: () => void;
}) {
  if (!label) {
    return <></>;
  }
  return (
    <div className={"flex flex-row gap-2"}>
      <button
        className={
          "flex flex-row gap-5 items-center border shadow-md rounded-md p-3 hover:bg-zinc-100"
        }
        onClick={onClick}
      >
        <div>{label}</div>
        <div>X</div>
      </button>
    </div>
  );
}
