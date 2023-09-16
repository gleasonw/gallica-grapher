export function Spinner({ isFetching }: { isFetching: boolean }) {
  return (
    <div className={"flex justify-center items-center"}>
      <div
        className={
          " h-4 w-4 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite] transition-opacity duration-150 " +
          (isFetching ? "opacity-100" : "opacity-0")
        }
        role="status"
      />
    </div>
  );
}
