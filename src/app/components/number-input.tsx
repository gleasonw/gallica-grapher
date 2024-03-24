import React from "react";
import { Input, InputProps } from "./design_system/input";

export interface NumberInputProps extends InputProps {
  children?: React.ReactNode;
  value?: number;
  onValueChange: (value: number) => void;
}

export function NumberInput(props: NumberInputProps) {
  return (
    <Input
      {...props}
      type="number"
      value={props.value}
      onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
        if (!isNaN(parseInt(e.target.value))) {
          props.onValueChange(parseInt(e.target.value));
        }
      }}
    />
  );
}
