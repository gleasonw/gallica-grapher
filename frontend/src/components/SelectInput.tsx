interface SelectInputProps<T extends string | number> {
  options: readonly T[];
  onChange: (value: string) => void;
  value?: string;
}
export function SelectInput<T extends string | number>(
  props: SelectInputProps<T>
) {
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
}
