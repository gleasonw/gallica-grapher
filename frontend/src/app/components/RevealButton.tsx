import React, { useState } from "react";

export const RevealButton: React.FC<{ label: string; onClick: () => void }> = (
  props
) => {
  const [expanded, setExpanded] = useState(false);
  return (
    <button
      className={"bg-white rounded-md shadow-sm p-3 border hover:bg-zinc-100"}
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
