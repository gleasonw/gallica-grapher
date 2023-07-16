"use client";

import { Link1Icon } from "@radix-ui/react-icons";
import React from "react";
import { YearRangeInput } from "../../components/YearRangeInput";
import InputBubble from "../../components/InputBubble";
import { SelectInput } from "../../components/SelectInput";
import {
  SearchPageState,
  searchStateReducer,
} from "../../components/SearchStateReducer";
import NavBar from "../../components/NavBar";
import {
  SearchPageDispatchContext,
  SearchPageStateContext,
} from "../../components/SearchContext";
import Image from "next/image";
import {
  ContextProps,
  OccurrenceContext,
} from "../../components/OccurrenceContext";
import { addQueryParamsIfExist } from "../../utils/addQueryParamsIfExist";
import { LangContext } from "../../components/LangContext";

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

export function SearchableContext(props: { initParams: SearchPageState }) {
  const [searchState, searchStateDispatch] = React.useReducer(
    searchStateReducer,
    props.initParams
  );

  const { lang } = React.useContext(LangContext);
  const translation = strings[lang];

  if (!searchState || !searchStateDispatch) {
    throw new Error("Search state not initialized");
  }
  const {
    yearRange,
    month,
    source,
    papers,
    limit,
    link_term: linkTerm,
    link_distance: linkDistance,
    sort,
    terms: term,
    tableFetchParams,
  } = searchState;

  function handleSubmit() {
    if (!term || !searchState) {
      return;
    }
    const baseUrl = `${window.location.pathname}`;
    const url = addQueryParamsIfExist(baseUrl, {
      terms: term,
      year: yearRange?.[0],
      end_year: yearRange?.[1],
      month,
      source,
      link_term: linkTerm,
      link_distance: linkDistance,
      sort,
      limit,
    });
    window.history.replaceState({}, "", url);
    const newProps: ContextProps = {
      codes: papers?.map((paper) => paper.code),
      link_distance: linkDistance,
      link_term: linkTerm,
      source,
      terms: [term],
      yearRange,
      month,
    };
    searchStateDispatch!({
      type: "set_table_props",
      payload: newProps,
    });
  }

  let contextParams: ContextProps = {} as ContextProps;
  if (props.initParams.terms && !tableFetchParams?.terms) {
    contextParams = {
      ...props.initParams,
      terms: [props.initParams.terms],
    };
  } else {
    contextParams = {
      ...tableFetchParams,
      all_context: true,
    };
  }

  function onSetLinkDistance(value?: number) {
    searchStateDispatch({
      type: "set_link_distance",
      payload: value,
    });
  }

  return (
    <SearchPageStateContext.Provider value={searchState}>
      <SearchPageDispatchContext.Provider value={searchStateDispatch}>
        <NavBar />
        <div
          className={
            "w-full flex flex-col justify-center gap-10 items-center rounded-lg pt-5 pb-5"
          }
        >
          <InputBubble
            word={term ?? ""}
            onWordChange={(word) =>
              searchStateDispatch({
                type: "set_terms",
                payload: word,
              })
            }
            onSubmit={handleSubmit}
          >
            <button
              className="bg-blue-700 text-sm pl-5 pr-5 hover:bg-blue-500 text-white absolute top-4 right-5 rounded-full p-3 shadow-md"
              onClick={handleSubmit}
            >
              Explore
            </button>
          </InputBubble>
          <div className={"flex flex-wrap gap-10 justify-center"}>
            <YearRangeInput
              min={1500}
              max={2023}
              value={yearRange}
              showLabel={true}
              onChange={(value) =>
                searchStateDispatch({
                  type: "set_context_range",
                  payload: value,
                })
              }
            />
            <SelectInput
              label={"corpus"}
              options={["book", "periodical", "all"]}
              value={source}
              onChange={(new_source) => {
                if (
                  new_source === "book" ||
                  new_source === "periodical" ||
                  new_source === "all"
                ) {
                  searchStateDispatch({
                    type: "set_source",
                    payload: new_source,
                  });
                }
              }}
            />
            <SelectInput
              label={"sort"}
              value={sort}
              options={["date", "relevance"]}
              onChange={(new_sort) => {
                if (new_sort === "date" || new_sort === "relevance") {
                  searchStateDispatch({
                    type: "set_sort",
                    payload: new_sort,
                  });
                }
              }}
            />
            <SelectInput
              label={"limit"}
              value={limit}
              options={[10, 20, 50]}
              onChange={(lim) => {
                const new_limit = parseInt(lim);
                if (typeof new_limit === "number") {
                  searchStateDispatch({
                    type: "set_limit",
                    payload: new_limit,
                  });
                }
              }}
            />
          </div>
          <div className="flex flex-wrap gap-5">
            <input
              type="text"
              value={linkTerm || ""}
              onChange={(e) =>
                searchStateDispatch({
                  type: "set_link_term",
                  payload: e.target.value,
                })
              }
              className={"border p-2 rounded-lg shadow-sm"}
              placeholder={translation.linkTerm}
            />
            <Link1Icon className="w-6 h-6" />
            <input
              type="number"
              value={linkDistance}
              onChange={(e) => {
                const numVal = parseInt(e.target.value);
                if (
                  typeof numVal === "number" &&
                  !isNaN(numVal) &&
                  numVal >= 0
                ) {
                  onSetLinkDistance!(numVal);
                } else if (e.target.value === "") {
                  onSetLinkDistance!(undefined);
                }
              }}
              className={"border p-2 rounded-lg shadow-sm"}
              placeholder={translation.linkDistance}
            />
          </div>
        </div>
        <OccurrenceContext {...contextParams} />
      </SearchPageDispatchContext.Provider>
    </SearchPageStateContext.Provider>
  );
}
