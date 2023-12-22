import React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../@/components/ui/select";
import { Label } from "../../@/components/ui/label";

export interface SelectBaseProps {
  children?: React.ReactNode;
  trigger?: React.ReactNode;
  value?: string;
  onChange?: (value: string) => void;
  className?: string;
  label: string;
}

export function SelectBase({
  children,
  trigger,
  value,
  onChange,
  className,
  label,
}: SelectBaseProps) {
  return (
    <Label className="flex flex-col gap-2">
      <span>{label}</span>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id="limit">{trigger}</SelectTrigger>
        <SelectContent position="popper">{children}</SelectContent>
      </Select>
    </Label>
  );
}
