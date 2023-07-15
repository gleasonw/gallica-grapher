import React from "react";

export function QueryPagination(props: {
  children: React.ReactNode;
  selectedPage: number;
  cursorMax: number;
  onFirstPage: () => void;
  onPageIncrement: () => void;
  onPageDecrement: () => void;
  onLastPage: () => void;
}) {
  return (
    <div
      className={
        "flex flex-row justify-center items-center text-xl md:text-2xl lg:text-2xl "
      }
    >
      <div
        className={
          "flex flex-row justify-between " +
          (props.selectedPage > 1 ? "opacity-100" : "opacity-0")
        }
      >
        <button onClick={props.onFirstPage} className={"p-3"}>
          {"<<"}
        </button>
        <button
          className={"p-4"}
          onClick={props.selectedPage > 1 ? props.onPageDecrement : undefined}
        >
          {"<"}
        </button>
      </div>
      {props.children}
      <div
        className={
          "flex flex-row justify-between " +
          (props.selectedPage <= props.cursorMax ? "opacity-100" : "opacity-0")
        }
      >
        <button
          className={"p-4"}
          onClick={
            props.selectedPage <= props.cursorMax
              ? props.onPageIncrement
              : undefined
          }
        >
          {">"}
        </button>
        <button onClick={props.onLastPage} className={"p-3"}>
          {">>"}
        </button>
      </div>
    </div>
  );
}
