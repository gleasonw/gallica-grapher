export function GallicaButton({
  children,
  onClick,
  className,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`hover:bg-gray-200 rounded shadow-sm p-3 border-2 cursor-pointer ${className}`}
    >
      {children}
    </button>
  );
}
