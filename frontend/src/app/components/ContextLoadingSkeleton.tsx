
export function ContextLoadingSkeleton() {
  return (
    <div className={"flex flex-col gap-20 md:m-5"}>
      {[...Array(10)].map((_, i) => (
        <div
          key={i}
          className={
            "animate-pulse md:border border-gray-400 md:shadow-lg md:rounded-lg md:p-10 flex flex-col gap-5 items-center w-full"
          }
        >
          <div className={"text-lg bg-gray-400 rounded h-6 w-3/4 mb-4"}></div>
          <div className={"bg-gray-400 rounded h-4 w-1/2 mb-4"}></div>
          <div className={"bg-gray-400 rounded h-4 w-1/4 mb-4"}></div>
          <div className={"bg-gray-400 rounded h-80 w-full mb-4"}></div>
        </div>
      ))}
    </div>
  );
}
