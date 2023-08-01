import { ContextQueryParams, fetchContext } from "./fetchContext";

export async function OCRTable({ params }: { params: ContextQueryParams }) {
  const data = await fetchContext(params);

  return (
    <>
      {data.records.map((record) => {
        <div key={record.url}>
          <h2>{record.paper_title}</h2>
          <h3>{record.date}</h3>
          <div className={"overflow-y-auto max-h-96"}>
            {record.context.map((context) => (
              <span key={context.page_url}>
                {context.left_context}{" "}
                <span className={"bg-yellow-200"}>{context.pivot}</span>{" "}
                {context.right_context}
              </span>
            ))}
          </div>
        </div>;
      })}
    </>
  );
}
