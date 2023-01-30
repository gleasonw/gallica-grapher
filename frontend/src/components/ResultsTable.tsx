import React from "react";
import { trpc } from "../utils/trpc";
import { Context } from "./Context";

export interface TableProps {
  terms?: string[];
  codes?: string[];
  day?: number | null;
  month?: number | null;
  year?: number | null;
  source?: "book" | "periodical" | "all" | null;
  link_term?: string | null;
  link_distance?: number | null;
  children?: React.ReactNode;
  limit?: number;
  sort?: "date" | "relevance" | null;
}

export const ResultsTable: React.FC<TableProps> = (props) => {
  const [selectedPage, setSelectedPage] = React.useState(1);
  const limit = props.limit || 20;
  const {
    isError,
    isLoading,
    fetchNextPage,
    fetchPreviousPage,
    isFetchingNextPage,
    isFetchingPreviousPage,
    ...data
  } = trpc.gallicaRecords.useInfiniteQuery(
    {
      year: props.year,
      month: props.month,
      day: props.day,
      codes: props.codes,
      terms: props.terms || [],
      source: props.source,
      link_term: props.link_term,
      link_distance: props.link_distance,
      limit: limit,
      sort: props.sort,
    },
    {
      staleTime: Infinity,
    }
  );

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return <div>Error</div>;
  }

  const currentPage = data.data?.pages.filter(
    (page) => page.nextCursor == pageToCursor(selectedPage)
  )[0];

  const total_results = Number(data.data?.pages[0].data.num_results) ?? 0;

  const cursorMax = Math.floor(total_results / limit) + 1;

  function pageToCursor(page: number) {
    return page * limit;
  }

  const fetchedCursors = data.data?.pages.map((page) => page.nextCursor);
  const fetchedSet = new Set(fetchedCursors);

  async function handleCursorIncrement(amount: number = 1) {
    if (fetchedSet && !fetchedSet.has(pageToCursor(selectedPage + amount))) {
      await fetchNextPage({
        pageParam: pageToCursor(selectedPage + amount - 1),
      });
    }
    setSelectedPage(selectedPage + amount);
  }

  async function handleCursorDecrement(amount: number = 1) {
    if (fetchedSet && !fetchedSet.has(pageToCursor(selectedPage - amount))) {
      await fetchPreviousPage({
        pageParam: pageToCursor(selectedPage - (amount + 1)),
      });
    }
    setSelectedPage(selectedPage - amount);
  }

  return (
    <div className={"flex flex-col"}>
      <div className={"m-auto ml-5 "}>{props.children}</div>
      <div className="bg-zinc-100">
        <div>
          <div className={"m-4 flex flex-col gap-5"}>
            <h1 className={"text-2xl"}>
              {isFetchingNextPage && <p>Fetching next page...</p>}
              {isFetchingPreviousPage && <p>Fetching previous page...</p>}
              {currentPage &&
                !isFetchingNextPage &&
                !isFetchingPreviousPage && (
                  <div>
                    <div
                      className={
                        "flex flex-row justify-center gap-10 text-xl md:text-3xl lg:text-3xl"
                      }
                    >
                      {selectedPage != 1 && (
                        <div className={"flex flex-row gap-10"}>
                          <button
                            onClick={() =>
                              handleCursorDecrement(selectedPage - 1)
                            }
                          >
                            {"<<"}
                          </button>
                          <button onClick={() => handleCursorDecrement()}>
                            {"<"}
                          </button>
                        </div>
                      )}
                      <CursorInput
                        cursor={selectedPage}
                        cursorMax={cursorMax}
                        onCursorIncrement={handleCursorIncrement}
                        onCursorDecrement={handleCursorDecrement}
                      />
                      <p>of {cursorMax.toLocaleString()}</p>
                      {selectedPage !== cursorMax && (
                        <div className={"flex flex-row gap-10"}>
                          <button onClick={() => handleCursorIncrement()}>
                            {">"}
                          </button>
                          <button
                            onClick={() =>
                              handleCursorIncrement(cursorMax - selectedPage)
                            }
                          >
                            {">>"}
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
            </h1>
            {currentPage?.data.records.map((record, index) => (
              <div
                key={index}
                className={"flex flex-col gap-5 bg-white p-5 shadow-md"}
              >
                <div className={"flex flex-row flex-wrap gap-10 pb-5 text-lg"}>
                  <p>{record.term}</p>
                  <p>{record.date}</p>
                  <p>{record.paper_title}</p>
                  <a
                    className={"truncate underline"}
                    href={record.url}
                    target={"_blank"}
                    rel={"noreferrer"}
                  >
                    {record.url}
                  </a>
                </div>
                <Context record={record} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

interface CursorInputProps {
  cursor: number;
  cursorMax: number;
  onCursorIncrement: (amount?: number) => void;
  onCursorDecrement: (amount?: number) => void;
}

const CursorInput: React.FC<CursorInputProps> = (props) => {
  const [localCursor, setLocalCursor] = React.useState(props.cursor);

  React.useEffect(() => {
    setLocalCursor(props.cursor);
  }, [props.cursor]);

  const handleLocalCursorChange = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = Number(e.target.value);

    let valueToPropagate = value;

    if (value > props.cursorMax) {
      valueToPropagate = props.cursorMax;
    }

    if (value <= 0) {
      valueToPropagate = 1;
    }

    if (valueToPropagate > props.cursor) {
      props.onCursorIncrement(valueToPropagate - props.cursor);
    } else if (valueToPropagate < props.cursor) {
      props.onCursorDecrement(props.cursor - valueToPropagate);
    }
    setLocalCursor(valueToPropagate);
  };

  return (
    <input
      type={"number"}
      value={localCursor}
      onChange={(e) => setLocalCursor(e.target.valueAsNumber)}
      className={"w-20"}
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          handleLocalCursorChange(e as any);
        }
      }}
    />
  );
};
