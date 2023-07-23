export default function InputBubble({
  word,
  onWordChange,
  onSubmit,
  children,
}: {
  word: string;
  onWordChange: (word: string) => void;
  onSubmit?: () => void;
  children?: React.ReactNode;
}) {
  return (
    <div className="text-2xl relative w-full max-w-3xl">
      <input
        className={"p-5 w-full rounded-3xl border-2 shadow-lg "}
        placeholder={"rechercher un mot"}
        value={word || ""}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
          onWordChange(e.target.value)
        }
        onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => {
          if (e.key === "Enter") {
            onSubmit?.();
          }
        }}
      />
      <div className={"m-5"}></div>
      {children}
    </div>
  );
}
