import React from "react";

interface SelectInputProps {
  options: string[];
  onChange: (value: string) => void;
  value?: string;
}
export const SelectInput: React.FC<SelectInputProps> = (props) => {
  return (
    <select
      className={"border rounded-lg bg-white p-3 hover:cursor-pointer"}
      onChange={(e) => props.onChange(e.target.value)}
      value={props.value}
    >
      {props.options.map((option, index: number) => (
        <option key={index} value={option}>
          {option}
        </option>
      ))}
    </select>
  );
};
