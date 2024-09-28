import React from "react";
import { Button } from "./design_system/button";
import { NumberInput } from "./number-input";

export function QueryPagination({
  selectedPage,
  cursorMax,
  onChange,
}: {
  selectedPage: number;
  cursorMax: number;
  onChange: (page: number) => void;
}) {
  return (
    <div className="flex w-full justify-between items-center mb-4 px-5">
      <section className=" flex gap-2 text-nowrap">
        Page
        <strong>{selectedPage}</strong>/ {cursorMax}
      </section>
      <section className="flex flex-row justify-between items-center gap-3">
        <div
          className={
            "flex flex-row justify-between " +
            (selectedPage > 1 ? "opacity-100" : "opacity-0")
          }
        >
          <Button
            variant="outline"
            onClick={() => onChange(1)}
            className={"p-3"}
          >
            {"<<"}
          </Button>
          <Button
            variant="outline"
            className={"p-4"}
            onClick={
              selectedPage > 1 ? () => onChange(selectedPage - 1) : undefined
            }
          >
            {"<"}
          </Button>
        </div>
        <p className={"mr-3 md:mr-5 lg:mr-5"}>Page</p>
        <CursorInput
          cursor={selectedPage}
          cursorMax={cursorMax}
          onChange={onChange}
          key={selectedPage}
        />
        <p className={"ml-3 md:ml-5 lg:ml-5 text-nowrap"}>
          / {(cursorMax + 1).toLocaleString()}
        </p>
        <div
          className={
            "flex flex-row justify-between " +
            (selectedPage <= cursorMax ? "opacity-100" : "opacity-0")
          }
        >
          <Button
            className={"p-4"}
            variant="outline"
            onClick={
              selectedPage <= cursorMax
                ? () => onChange(selectedPage + 1)
                : undefined
            }
          >
            {">"}
          </Button>
          <Button
            variant="outline"
            onClick={() => onChange(cursorMax + 1)}
            className={"p-3"}
          >
            {">>"}
          </Button>
        </div>
      </section>
    </div>
  );
}

export interface CursorInputProps {
  cursor: number;
  cursorMax: number;
  onChange: (cursor: number) => void;
}

export function CursorInput({ cursor, cursorMax, onChange }: CursorInputProps) {
  const [localCursor, setLocalCursor] = React.useState(cursor);

  const handleLocalCursorChange = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = Number(e.target.value);

    let valueToPropagate = value;

    if (value > cursorMax) {
      valueToPropagate = cursorMax;
    }

    if (value <= 0) {
      valueToPropagate = 1;
    }

    if (valueToPropagate > cursor) {
      onChange(valueToPropagate);
    } else if (valueToPropagate < cursor) {
      onChange(valueToPropagate);
    }
    setLocalCursor(valueToPropagate);
  };

  return (
    <NumberInput
      className="w-20"
      value={localCursor}
      onValueChange={(cursor) => setLocalCursor(cursor)}
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          handleLocalCursorChange(e as any);
        }
      }}
    />
  );
}
