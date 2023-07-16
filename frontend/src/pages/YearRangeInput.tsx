import React, { useContext } from "react";
import { LangContext } from "../components/LangContext";

export interface YearRangeInputProps {
  min: number;
  max: number;
  value?: [number?, number?];
  placeholder?: [number, number];
  onChange: (value?: [number?, number?]) => void;
  showLabel?: boolean;
}

export function YearRangeInput(props: YearRangeInputProps) {
  const { lang } = useContext(LangContext);
  const [expanded, setExpanded] = React.useState(false);
  const [localValue, setLocalValue] = React.useState(props.value);
  return (
    <div className={"relative"}>
      {props.showLabel && (
        <label
          htmlFor={"year-range"}
          className="block text-gray-700 text-sm font-bold"
        >
          {lang === "fr" ? "Années" : "Years"}
        </label>
      )}
      {expanded && (
        <div
          className={
            "flex flex-col text-md max-w-md items-center gap-5 p-3 border rounded-lg absolute top-0 -left-10 bg-white z-40"
          }
          id={"year-range"}
        >
          <div className={"flex gap-5 items-center"}>
            <input
              className="w-20 border p-3  rounded-md"
              type="number"
              value={localValue?.[0] || ""}
              onChange={(e) => {
                const newValue = parseInt(e.target.value);
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
                const newValue = parseInt(e.target.value);
                if (typeof newValue === "number") {
                  setLocalValue([localValue?.[0], newValue]);
                }
              }}
              placeholder={props.placeholder?.[1].toString()}
            />
          </div>
          <div className={"flex gap-5 items-center"}>
            <button
              className={"p-2 text-blue-500"}
              onClick={() => {
                setExpanded(false);
              }}
            >
              {lang === "fr" ? "Annuler" : "Cancel"}
            </button>
            <button
              className={"border p-2 hover:bg-blue-100 rounded-md"}
              onClick={() => {
                props.onChange(localValue);
                setExpanded(false);
              }}
            >
              Apply
            </button>
          </div>
        </div>
      )}
      <div
        className={
          "flex flex-row text-md items-center gap-5 p-3 cursor-pointer bg-blue-100 rounded-xl"
        }
        id={"year-range"}
        onClick={() => setExpanded(true)}
      >
        <span className={""}>{props.value?.[0] || props.placeholder?.[0]}</span>
        <span className={""}>to</span>
        <span className={""}>{props.value?.[1] || props.placeholder?.[1]}</span>
        ⌄
      </div>
    </div>
  );
}
