type SelectOptions = readonly string[] | readonly number[];

type Option<T extends SelectOptions> = T extends readonly (infer ElementType)[]
  ? ElementType
  : never;

interface SelectInputProps<T extends SelectOptions> {
  options: T;
  onChange: (value: Option<T>) => void;
  value?: Option<T>;
  label?: string;
}
export function SelectInput<T extends SelectOptions>({
  options,
  onChange,
  value,
  label,
}: SelectInputProps<T>) {
  return (
    <div className={"flex flex-col"}>
      <label htmlFor={label} className="block text-gray-700 text-sm font-bold">
        {label}
      </label>
      <select
        className={"border rounded-lg bg-white p-3 hover:cursor-pointer"}
        onChange={(e) => {
          if (typeof options[0] === "number") {
            onChange(parseInt(e.target.value) as Option<T>);
          } else {
            onChange(e.target.value as Option<T>);
          }
        }}
        value={value}
        id={label || ""}
      >
        {options.map((option, index: number) => (
          <option key={index} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}
