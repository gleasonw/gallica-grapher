"use client";

import React from "react";
import { useSearchState } from "../composables/useSearchState";
import { QueryPagination } from "./QueryPagination";
import { useSubmit } from "./LoadingProvider";
import * as Tabs from "@radix-ui/react-tabs";
import { useSelectedTerm } from "../composables/useSelectedTerm";

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
  const [locallySelectedPage, setLocallySelectedPage] =
    React.useState<number>(1);
  const translation = strings["fr"];
  const searchState = useSearchState();
  const { terms, year, end_year, month, cursor, context_year } = searchState;

  const selectedTerm = useSelectedTerm();

  const [localTab, setLocalTab] = React.useState<string | undefined>(
    selectedTerm
  );

  const currentPage = Math.floor((cursor ?? 0) / 10) + 1;

  const totalPages = Math.floor((numResults ?? 0) / 10);

  const { handleSubmit, isPending } = useSubmit();

  const referenceTab = isPending ? localTab : selectedTerm;

  function setNewPage(newPage: number) {
    setLocallySelectedPage(newPage);
    handleSubmit({
      cursor: (newPage - 1) * 10,
    });
  }

  const referencePage = isPending ? locallySelectedPage : currentPage;

  if (!isPending && referenceTab !== localTab) {
    setLocalTab(referenceTab);
  }

  if (!isPending && referencePage !== currentPage) {
    setLocallySelectedPage(currentPage);
  }

  return (
    <div>
      <div className={"flex flex-col gap-5 ml-5 mr-5 mt-2"}>
        <div className={"flex wrap gap-10"}>
          <ContextFilter
            onClick={() => {
              setLocallySelectedPage(1);
              handleSubmit({
                year: undefined,
                end_year: undefined,
                context_year: undefined,
                cursor: 0,
              });
            }}
            label={
              context_year
                ? `${context_year}`
                : year && end_year
                  ? `${year} - ${end_year}`
                  : undefined
            }
          />
          <ContextFilter
            label={month ? translation.months[month - 1] : undefined}
            onClick={() => {
              setLocallySelectedPage(1);
              handleSubmit({ month: undefined, cursor: 0 });
            }}
          />
        </div>
      </div>
      <Tabs.Root
        value={referenceTab}
        onValueChange={(value) => {
          setLocallySelectedPage(1);
          setLocalTab(value);
          handleSubmit({ selected_term: value, cursor: 0 });
        }}
      >
        <Tabs.List className={"flex flex-row gap-3 w-full border-b pl-2"}>
          {(terms ?? ["brazza"])?.map((term) => (
            <Tabs.Trigger
              value={term}
              key={term}
              className={`p-5 transition-all focus:outline-1 ${
                referenceTab === term && "border-b-2 border-blue-500"
              }`}
            >
              {term}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <QueryPagination
          cursorMax={totalPages}
          selectedPage={referencePage ?? 1}
          onChange={setNewPage}
        />
        {(terms ?? ["brazza"])?.map((term) => (
          <Tabs.Content
            value={term}
            key={term}
            className={isPending ? "opacity-50 transition-all" : ""}
          >
            {children}
          </Tabs.Content>
        ))}
      </Tabs.Root>
    </div>
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
