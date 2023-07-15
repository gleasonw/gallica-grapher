import React from "react";

export interface CursorInputProps {
  cursor: number;
  cursorMax: number;
  onCursorIncrement: (amount: number) => void;
  onCursorDecrement: (amount: number) => void;
}

export function CursorInput(props: CursorInputProps) {
  const [localCursor, setLocalCursor] = React.useState(props.cursor);

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
      props.onCursorIncrement(valueToPropagate);
    } else if (valueToPropagate < props.cursor) {
      props.onCursorDecrement(valueToPropagate);
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
