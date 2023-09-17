import React, { useContext } from "react";
import * as Popover from "@radix-ui/react-popover";

export interface YearRangeInputProps {
  min: number;
  max: number;
  value: [number?, number?];
  placeholder?: [number, number];
  onChange: (value: [number?, number?]) => void;
  showLabel?: boolean;
}

export function YearRangeInput(props: YearRangeInputProps) {
  const lang = "fr";
  const [localValue, setLocalValue] = React.useState(props.value);
  return (
    <Popover.Root>
      <Popover.Trigger>
        {props.showLabel && (
          <label
            htmlFor={"year-range"}
            className="block text-gray-700 text-sm font-bold"
          >
            {lang === "fr" ? "Années" : "Years"}
          </label>
        )}
        <div
          className={
            "flex flex-row text-md items-center gap-5 p-3 cursor-pointer rounded-xl shadow-md"
          }
          id={"year-range"}
        >
          <span className={""}>
            {props.value?.[0] || props.placeholder?.[0]}
          </span>
          <span className={""}>to</span>
          <span className={""}>
            {props.value?.[1] || props.placeholder?.[1]}
          </span>
          ⌄
        </div>
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Content>
          <div className={"relative"}>
            <div
              className={
                "flex flex-col text-md max-w-md items-center gap-5 p-3 border rounded-lg top-0 -left-10 bg-white z-40"
              }
              id={"year-range"}
            >
              <div className={"flex gap-5 items-center"}>
                <input
                  className="w-20 border p-3 rounded-md"
                  type="number"
                  value={localValue?.[0] || ""}
                  onChange={(e) => {
                    const newValue = e.target.valueAsNumber;
                    if (typeof newValue === "number") {
                      setLocalValue([newValue, localValue?.[1]]);
                    }
                  }}
                  placeholder={props.placeholder?.[0].toString()}
                />
                {lang === "fr" ? "à" : "to"}
                <input
                  className="w-20 p-3 rounded-md border"
                  type="number"
                  value={localValue?.[1] || ""}
                  onChange={(e) => {
                    const newValue = e.target.valueAsNumber;
                    if (typeof newValue === "number") {
                      setLocalValue([localValue?.[0], newValue]);
                    }
                  }}
                  placeholder={props.placeholder?.[1].toString()}
                />
              </div>
              <div className={"flex gap-5 items-center"}>
                <button
                  className={"border p-2 hover:bg-blue-100 rounded-md"}
                  onClick={() => props.onChange(localValue)}
                >
                  Apply
                </button>
              </div>
            </div>
          </div>
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}
