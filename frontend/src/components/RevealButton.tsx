import React, { useState } from "react";

export const RevealButton: React.FC<{ label: string; onClick: () => void }> = (
  props
) => {
  const [expanded, setExpanded] = useState(false);
  return (
    <button
      className={"border p-5 hover:bg-zinc-100"}
      onClick={() => {
        props.onClick();
        setExpanded(!expanded);
      }}
    >
      {expanded ? (
        <span>X</span>
      ) : (
        <span>{props.label} ⌄</span>
      )}
    </button>
  );
};
