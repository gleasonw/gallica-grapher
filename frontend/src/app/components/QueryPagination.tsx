import React from "react";

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
    <div
      className={
        "flex flex-row justify-center items-center text-xl md:text-2xl lg:text-2xl "
      }
    >
      <div
        className={
          "flex flex-row justify-between " +
          (selectedPage > 1 ? "opacity-100" : "opacity-0")
        }
      >
        <button onClick={() => onChange(1)} className={"p-3"}>
          {"<<"}
        </button>
        <button
          className={"p-4"}
          onClick={
            selectedPage > 1 ? () => onChange(selectedPage - 1) : undefined
          }
        >
          {"<"}
        </button>
      </div>
      <p className={"mr-3 md:mr-5 lg:mr-5"}>Page</p>
      <CursorInput
        cursor={selectedPage}
        cursorMax={cursorMax}
        onChange={onChange}
        key={selectedPage}
      />
      <p className={"ml-3 md:ml-5 lg:ml-5"}>
        / {(cursorMax + 1).toLocaleString()}
      </p>
      <div
        className={
          "flex flex-row justify-between " +
          (selectedPage <= cursorMax ? "opacity-100" : "opacity-0")
        }
      >
        <button
          className={"p-4"}
          onClick={
            selectedPage <= cursorMax
              ? () => onChange(selectedPage + 1)
              : undefined
          }
        >
          {">"}
        </button>
        <button onClick={() => onChange(cursorMax + 1)} className={"p-3"}>
          {">>"}
        </button>
      </div>
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
    <input
      type={"number"}
      value={localCursor}
      onChange={(e) => setLocalCursor(e.target.valueAsNumber)}
      className={"w-full max-w-max border rounded-md"}
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          handleLocalCursorChange(e as any);
        }
      }}
    />
  );
}
