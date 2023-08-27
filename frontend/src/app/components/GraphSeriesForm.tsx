"use client";

import React, { Suspense, useState } from "react";
import { seriesColors } from "./utils/makeHighcharts";
import InputBubble from "./InputBubble";
import { YearRangeInput } from "./YearRangeInput";
import { useSearchState } from "../composables/useSearchState";
import { useSubmit } from "./LoadingProvider";
import { Spinner } from "./Spinner";
import { useSelectedTerm } from "../composables/useSelectedTerm";

type GraphFormState = {
  word: string;
  source: "presse" | "livres" | "tout";
  link_term: string;
  year?: number;
  end_year?: number;
};

export function GraphSeriesForm({
  children,
  lineChart,
  proximityBar,
}: {
  children?: React.ReactNode;
  lineChart: React.ReactNode;
  proximityBar?: React.ReactNode;
}) {
  const [graphFormState, setGraphFormState] = useState<GraphFormState>({
    word: "",
    source: "presse",
    link_term: "",
    year: 1789,
    end_year: 1950,
  });

  const { word, source, link_term, year, end_year } = graphFormState;
  const { terms, context_year, month } = useSearchState();
  const selectedTerm = useSelectedTerm();

  const { handleSubmit, isPending } = useSubmit();

  const sourceOptions = ["presse", "livres", "tout"] as const;

  function translateSource(source: (typeof sourceOptions)[number]) {
    switch (source) {
      case "presse":
        return "periodical";
      case "livres":
        return "book";
      case "tout":
        return "all";
    }
  }

  return (
    <>
      <form
        className={
          "w-full flex flex-col justify-center items-center rounded-full gap-5"
        }
        onSubmit={(e) => {
          e.preventDefault();
          setGraphFormState({
            ...graphFormState,
            word: "",
          });
          handleSubmit({
            terms: terms ? [...terms, word] : [word],
            link_term,
            end_year,
            year,
            source: translateSource(source),
          });
        }}
      >
        <InputBubble
          word={word}
          onWordChange={(word) =>
            setGraphFormState({ ...graphFormState, word })
          }
        >
          <button className="bg-blue-700 text-sm pl-5 pr-5 hover:bg-blue-500 text-white absolute top-4 right-5 rounded-full p-3 shadow-md">
            {isPending ? <Spinner isFetching /> : "Explore"}
          </button>
        </InputBubble>
        <div className={"flex flex-wrap gap-10 items-center justify-center"}>
          <YearRangeInput
            max={2021}
            min={1500}
            value={[year, end_year]}
            onChange={([newYear, newEndYear]) =>
              handleSubmit({
                year: newYear,
                end_year: newEndYear,
              })
            }
            placeholder={[1789, 1950]}
          />
        </div>
      </form>
      <div className={"m-2"} />
      <TicketRow />
      <div className={"m-2"} />

      <Suspense
        key={terms && [...terms, year, end_year].join("-")}
        fallback={<div>Chargement du graphe...</div>}
      >
        {lineChart}
      </Suspense>
      <p className={"m-2"}>
        Données de graph fournies par{" "}
        <a
          href="https://shiny.ens-paris-saclay.fr/app/gallicagram"
          target="_blank"
          rel="noreferrer"
          className="text-blue-500 underline"
        >
          Gallicagram
        </a>
        , un projet de Benjamin Azoulay et Benoît de Courson.
      </p>
      {proximityBar && (
        <Suspense
          key={`${selectedTerm}-${context_year}-${terms?.join("-")}-${month}`}
          fallback={<BarSkeleton />}
        >
          {proximityBar}
        </Suspense>
      )}

      {children}
    </>
  );
}

function BarSkeleton() {
  return (
    <div className="p-6 space-y-4 flex flex-col">
      <div className="w-10/12 h-4 bg-gray-200 rounded animate-pulse" />
      <div className="w-7/12 h-4 bg-gray-200 rounded animate-pulse" />
      <div className="w-6/12 h-4 bg-gray-200 rounded animate-pulse" />
      <div className="w-4/12 h-4 bg-gray-200 rounded animate-pulse" />
      <div className="w-3/12 h-4 bg-gray-200 rounded animate-pulse" />
      <div className="w-2/12 h-4 bg-gray-200 rounded animate-pulse" />
    </div>
  );
}

function TicketRow(props: { children?: React.ReactNode }) {
  const { terms } = useSearchState();
  const { handleSubmit } = useSubmit();
  const displayTerms = terms ?? ["brazza"];
  return (
    <div className={"z-0 flex self-start m-5"}>
      <div className={"flex flex-wrap gap-10"}>
        {displayTerms?.map((term, index) => (
          <button
            onClick={() =>
              handleSubmit({
                terms: terms?.filter((t) => t !== term),
                selected_term: undefined,
              })
            }
            className={`rounded-lg border-2 bg-white p-3 text-xl shadow-md transition duration-150 hover:bg-zinc-500 hover:ease-in`}
            style={{ borderColor: seriesColors[index % seriesColors.length] }}
            key={term}
          >
            <div className={`relative h-full w-full flex flex-col`}>
              <div className={"flex flex-row gap-10"}>
                <p>{term}</p>
                <p className={"text-zinc-600"}>x</p>
              </div>
            </div>
          </button>
        ))}
      </div>
      {props.children}
    </div>
  );
}
