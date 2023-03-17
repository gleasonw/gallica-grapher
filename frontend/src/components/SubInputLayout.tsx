import React from "react";

export function SubInputLayout(props: { children: React.ReactNode; }) {
  return (
    <div className="flex flex-wrap gap-5 items-center rounded-lg bg-white p-3 shadow-sm border">
      {props.children}
    </div>
  );
}
