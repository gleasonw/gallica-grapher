import { useState } from "react";
import { ImageTable } from "./ImageTable";
import { OCRTable, TableProps } from "./OCRTable";
import * as ToggleGroup from "@radix-ui/react-toggle-group";

export function OccurrenceContext(props: TableProps) {
  const [contextType, setContextType] = useState<"ocr" | "image">("image");

  return (
    <>
      <ToggleGroup.Root
        type="single"
        value={contextType}
        onValueChange={(value) => setContextType(value as "ocr" | "image")}
        className={
          "flex ml-5 mr-5 mt-2 border border-gray-300 shadow-md w-fit rounded-lg"
        }
      >
        <ToggleGroup.Item
          value="ocr"
          className={`p-5 hover:bg-gray-200 transition-colors ${
            contextType === "ocr" ? "bg-gray-200" : ""
          }`}
        >
          OCR
        </ToggleGroup.Item>
        <span className={"border-l border-gray-300"} />
        <ToggleGroup.Item
          value="image"
          className={`p-5 hover:bg-gray-200 transition-colors ${
            contextType === "image" ? "bg-gray-200" : ""
          }`}
        >
          Image
        </ToggleGroup.Item>
      </ToggleGroup.Root>
      {contextType === "ocr" ? (
        <OCRTable {...props}>{props.children}</OCRTable>
      ) : (
        <ImageTable {...props}>{props.children}</ImageTable>
      )}
    </>
  );
}
