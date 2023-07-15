import { useState } from "react";
import { ContextTypeToggle } from "./ContextTypeToggle";
import { ImageTable } from "./ImageTable";
import { OCRTable, TableProps } from "./OCRTable";

export function OccurrenceContext(props: TableProps) {
  const [contextType, setContextType] = useState<"ocr" | "image">("image");

  return (
    <>
      <ContextTypeToggle value={contextType} onChange={setContextType} />
      {contextType === "ocr" ? (
        <OCRTable {...props}>{props.children}</OCRTable>
      ) : (
        <ImageTable {...props}>{props.children}</ImageTable>
      )}
    </>
  );
}
