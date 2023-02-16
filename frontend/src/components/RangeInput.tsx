import React, { useContext } from "react";
import { LangContext } from "../pages";

interface RangeInputProps {
  min: number;
  max: number;
  value: [number, number];
  onChange: (value: [number, number]) => void;
}
export const RangeInput: React.FC<RangeInputProps> = (props) => {
  const { lang } = useContext(LangContext);
  return (
    <div className={"flex flex-row flex-wrap gap-10 rounded-md border-4 shadow-sm p-5"}>
      {lang === "fr" ? "De" : "From"}
      <input
        className="w-20"
        type="number"
        value={props.value[0]}
        onChange={(e) => {
          const newValue = [parseInt(e.target.value), props.value[1]];
          props.onChange(newValue as [number, number]);
        }}
      />
      {lang === "fr" ? "à" : "to"}
      <input
        className="w-20"
        type="number"
        value={props.value[1]}
        onChange={(e) => {
          const newValue = [props.value[0], parseInt(e.target.value)];
          props.onChange(newValue as [number, number]);
        }}
      />
    </div>
  );
};
