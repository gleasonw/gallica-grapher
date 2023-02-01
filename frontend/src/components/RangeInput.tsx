import React, { useEffect } from "react";
import { RevealButton } from "./RevealButton";

interface RangeInputProps {
  min: number;
  max: number;
  value: [number, number];
  onChange: (value: [number, number]) => void;
}
export const RangeInput: React.FC<RangeInputProps> = (props) => {
  return (
    <div className={"flex flex-row flex-wrap gap-10 rounded-md border-4 p-5"}>
      Between
      <input
        className="w-20"
        type="number"
        value={props.value[0]}
        onChange={(e) => {
          const newValue = [parseInt(e.target.value), props.value[1]];
          props.onChange(newValue as [number, number]);
        }}
      />
      and
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
