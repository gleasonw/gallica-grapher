interface SelectInputProps<T extends string | number> {
  options: readonly T[];
  onChange: (value: string) => void;
  value?: T;
  label?: string;
}
export function SelectInput<T extends string | number>(
  props: SelectInputProps<T>
) {
  return (
    <div className={"flex flex-col"}>
      <label
        htmlFor={props.label}
        className="block text-gray-700 text-sm font-bold mb-2"
      >
        {props.label}
      </label>
      <select
        className={"border rounded-lg bg-white p-3 hover:cursor-pointer"}
        onChange={(e) => props.onChange(e.target.value)}
        value={props.value}
        id={props.label || ""}
      >
        {props.options.map((option, index: number) => (
          <option key={index} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}
