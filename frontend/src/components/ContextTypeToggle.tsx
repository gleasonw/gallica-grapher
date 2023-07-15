import * as ToggleGroup from "@radix-ui/react-toggle-group";

export function ContextTypeToggle({
  value,
  onChange,
}: {
  value: "ocr" | "image";
  onChange: (new_value: "ocr" | "image") => void;
}) {
  return (
    <ToggleGroup.Root
      type="single"
      value={value}
      onValueChange={(value) => onChange(value as "ocr" | "image")}
      className={
        "flex ml-5 mr-5 mt-2 border border-gray-300 shadow-md w-fit rounded-lg"
      }
    >
      <ToggleGroup.Item
        value="ocr"
        className={`p-5 hover:bg-gray-200 transition-colors ${
          value === "ocr" ? "bg-gray-200" : ""
        }`}
      >
        OCR
      </ToggleGroup.Item>
      <span className={"border-l border-gray-300"} />
      <ToggleGroup.Item
        value="image"
        className={`p-5 hover:bg-gray-200 transition-colors ${
          value === "image" ? "bg-gray-200" : ""
        }`}
      >
        Image
      </ToggleGroup.Item>
    </ToggleGroup.Root>
  );
}
