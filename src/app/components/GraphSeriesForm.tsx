"use client";

import React from "react";
import { seriesColors } from "./utils/makeHighcharts";
import InputBubble from "./InputBubble";
import { YearRangeInput } from "./YearRangeInput";
import { useSearchState } from "../composables/useSearchState";
import { useSubmit } from "./LoadingProvider";
import { Spinner } from "./Spinner";
import { SearchState } from "../utils/searchState";

export function GraphSeriesForm({ children }: { children?: React.ReactNode }) {
  const { terms, year, end_year } = useSearchState();
  const [localTerm, setLocalTerm] = React.useState<string>("");

  const { handleSubmit, isPending } = useSubmit();

  function submitForm(args?: unknown) {
    if (typeof args === "object")
      handleSubmit({
        ...args,
        terms: terms ? [...terms, localTerm] : [localTerm],
      });
  }

  return (
    <>
      <form
        className={
          "w-full flex flex-col justify-center items-center rounded-full gap-5"
        }
        onSubmit={(e) => {
          e.preventDefault();
          submitForm();
        }}
      >
        <InputBubble
          word={localTerm}
          onWordChange={(word) => setLocalTerm(word)}
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
              submitForm({
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
      {children}
    </>
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
