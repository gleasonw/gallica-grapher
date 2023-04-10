import { ResultsTable, TableProps } from "../../components/ResultsTable";
import React from "react";
import { YearRangeInput } from "..";
import DashboardLayout from "../../components/DashboardLayout";
import InputBubble from "../../components/InputBubble";
import { PaperSelector } from "../../components/PaperSelector";
import { SelectInput } from "../../components/SelectInput";
import { SubInputLayout } from "../../components/SubInputLayout";
import {
  SearchPageState,
  searchStateReducer,
} from "../../components/SearchStateReducer";
import NavBar from "../../components/NavBar";
import {
  SearchPageDispatchContext,
  SearchPageStateContext,
} from "../../components/SearchContext";
import { z } from "zod";
import { useRouter } from "next/router";
import Head from "next/head";
import { ProximitySearchInput } from "../../components/ProximitySearchInput";

const searchPageState = z.object({
  terms: z.string(),
  year: z.coerce.number().nullish(),
  end_year: z.coerce.number().nullish(),
  day: z.coerce.number().nullish(),
  source: z
    .literal("book")
    .or(z.literal("periodical"))
    .or(z.literal("all"))
    .nullish(),
  link_term: z.string().nullish(),
  link_distance: z.coerce.number().nullish(),
  codes: z.string().array().nullish(),
  limit: z.coerce.number().nullish(),
  sort: z.literal("date").or(z.literal("relevance")).nullish(),
  cursor: z.number().nullish(),
});

export default function Context() {
  const router = useRouter();
  const result = searchPageState.safeParse(router.query);

  return (
    <>
      <Head>
        <title>Gallica Context</title>
        <meta
          name="View context surrounding occurrences of words in the French national archive."
          content="Gallica Context"
        />
      </Head>
      <NavBar />
      {result.success ? (
        <SearchableContext
          initParams={{
            terms: result.data.terms,
            papers: undefined,
            source: result.data.source ?? "all",
            limit: result.data.limit ?? undefined,
            cursor: result.data.cursor ?? undefined,
            yearRange: result.data.year
              ? [result.data.year, result.data.end_year ?? undefined]
              : [undefined, undefined],
            sort: result.data.sort ?? undefined,
            link_term: result.data.link_term ?? undefined,
            link_distance: result.data.link_distance ?? undefined,
          }}
          key={JSON.stringify(router.query)}
        />
      ) : (
        <SearchableContext
          initParams={{
            terms: "",
            papers: undefined,
            source: "all",
            limit: undefined,
            cursor: undefined,
            yearRange: undefined,
            sort: undefined,
            link_term: undefined,
            link_distance: undefined,
          }}
          key={JSON.stringify(router.query)}
        />
      )}
    </>
  );
}

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

function SearchableContext(props: { initParams: SearchPageState }) {
  console.log(props.initParams);
  const [searchState, searchStateDispatch] = React.useReducer(
    searchStateReducer,
    props.initParams
  );

  if (!searchState || !searchStateDispatch) {
    throw new Error("Search state not initialized");
  }
  const {
    yearRange,
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
    const params = new URLSearchParams();
    const searchStateKeys = Object.keys(searchState) as Array<
      keyof SearchPageState
    >;
    for (const key of searchStateKeys) {
      if (
        key === "papers" ||
        key === "yearRange" ||
        key === "tableFetchParams"
      ) {
        continue;
      }
      if (searchState[key] !== "" && searchState[key] !== undefined) {
        const stringified = searchState[key]?.toString();
        if (stringified) {
          params.append(key, stringified);
        }
      }
    }
    if (searchState.yearRange) {
      const [start, end] = searchState.yearRange;
      if (start) {
        params.append("year", start.toString());
      }
      if (end) {
        params.append("end_year", end.toString());
      }
    }
    window.history.replaceState(
      {},
      "",
      `${window.location.pathname}?${params.toString()}`
    );
    const newProps: TableProps = {
      limit,
      codes: papers?.map((paper) => paper.code),
      link_distance: linkDistance,
      link_term: linkTerm,
      sort,
      source,
      terms: [term],
      yearRange,
    };
    searchStateDispatch!({
      type: "set_table_props",
      payload: newProps,
    });
  }
  console.log(searchState.terms);

  return (
    <SearchPageStateContext.Provider value={searchState}>
      <SearchPageDispatchContext.Provider value={searchStateDispatch}>
        <DashboardLayout>
          <div
            className={
              "w-full flex flex-col justify-center gap-10 items-center rounded-lg pt-5 pb-5"
            }
          >
            <InputBubble
              word={term}
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
              <SubInputLayout>
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
              </SubInputLayout>
              <SubInputLayout>
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
                {source === "periodical" && (
                  <PaperSelector
                    papers={papers}
                    from={yearRange?.[0]}
                    to={yearRange?.[1]}
                    onPaperAdd={(new_paper) =>
                      searchStateDispatch({
                        type: "add_paper",
                        payload: new_paper,
                      })
                    }
                    onPaperClick={(paperCode) => {
                      searchStateDispatch({
                        type: "remove_paper",
                        payload: paperCode.code,
                      });
                    }}
                  />
                )}
              </SubInputLayout>
              <SubInputLayout>
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
              </SubInputLayout>
            </div>
            <div
              className={
                !term
                  ? "opacity-0 transition-opacity duration-500"
                  : "opacity-100 transition-opacity duration-500"
              }
            >
              <ProximitySearchInput
                linkTerm={linkTerm}
                linkDistance={linkDistance}
                onSetLinkDistance={(new_distance) =>
                  searchStateDispatch({
                    type: "set_link_distance",
                    payload: new_distance,
                  })
                }
                onSetLinkTerm={(new_term) =>
                  searchStateDispatch({
                    type: "set_link_term",
                    payload: new_term,
                  })
                }
              />
            </div>
          </div>
        </DashboardLayout>
        {tableFetchParams ? (
          <ResultsTable {...{ ...tableFetchParams, all_context: true }} />
        ) : (
          props.initParams.terms !== "" && (
            <ResultsTable
              {...{
                ...props.initParams,
                terms: [props.initParams.terms],
              }}
            />
          )
        )}
      </SearchPageDispatchContext.Provider>
    </SearchPageStateContext.Provider>
  );
}
