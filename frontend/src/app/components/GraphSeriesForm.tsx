"use client";

import React, { useState } from "react";
import { seriesColors } from "./utils/makeHighcharts";
import InputBubble from "./InputBubble";
import { YearRangeInput } from "./YearRangeInput";
import { SelectInput } from "./SelectInput";
import { useSearchState } from "../composables/useSearchState";
import { useSubmit } from "./LoadingProvider";

type GraphFormState = {
  word: string;
  source: "presse" | "livres" | "tout";
  link_term: string;
  year?: number;
  end_year?: number;
};

export function GraphSeriesForm({ children }: { children: React.ReactNode }) {
  const [graphFormState, setGraphFormState] = useState<GraphFormState>({
    word: "",
    source: "presse",
    link_term: "",
    year: 1789,
    end_year: 1950,
  });

  const { word, source, link_term, year, end_year } = graphFormState;
  const { terms } = useSearchState();

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
            Explore
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
          {/* <SelectInput
            options={["presse", "livres", "tout"] as const}
            value={source}
            onChange={(newValue) =>
              setGraphFormState({ ...graphFormState, source: newValue })
            }
          />
          <input
            type="text"
            className={"border p-2 rounded-lg shadow-sm"}
            value={link_term}
            placeholder={"Proximité (3)"}
            onChange={(e) =>
              setGraphFormState({
                ...graphFormState,
                link_term: e.target.value,
              })
            }
          /> */}
        </div>
      </form>
      <div className={"m-2"} />
      <TicketRow />
      <div className={"m-2"} />
      <div className={isPending ? "opacity-50 transition-all" : ""}>
        {children}
      </div>
    </>
  );
}

function TicketRow(props: { children?: React.ReactNode }) {
  const { terms } = useSearchState();
  const { handleSubmit } = useSubmit();
  return (
    <div className={"z-0 flex self-start m-5"}>
      <div className={"flex flex-wrap gap-10"}>
        {terms?.map((term, index) => (
          <button
            onClick={() =>
              handleSubmit({ terms: terms.filter((t) => t !== term) })
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
