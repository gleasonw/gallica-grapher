"use client";
import * as ToggleGroup from "@radix-ui/react-toggle-group";

type SelectOptions = readonly string[];

type Option<T extends SelectOptions> = T extends readonly (infer ElementType)[]
  ? ElementType
  : never;

type ToggleProps<T extends SelectOptions> = {
  options: T;
  onChange: (value: Option<T>) => void;
  value: Option<T>;
};

export function ToggleOptions<T extends SelectOptions>({
  options,
  onChange,
  value,
}: ToggleProps<T>) {
  return (
    <ToggleGroup.Root
      type={"single"}
      value={value}
      onValueChange={(value) => onChange(value as Option<T>)}
      className={
        "flex ml-5 mr-5 mt-2 border border-gray-300 shadow-md w-fit rounded-lg"
      }
    >
      {options.map((option, index) => (
        <div key={option}>
          <ToggleGroup.Item
            value={option}
            className={`p-5 hover:bg-gray-200 transition-colors ${
              value === option ? "bg-gray-200" : ""
            }`}
          >
            {option}
          </ToggleGroup.Item>
          {index !== options.length - 1 && (
            <span className={"border-l border-gray-300"} />
          )}
        </div>
      ))}
    </ToggleGroup.Root>
  );
}
