import React from "react";

export function SubInputLayout(props: { children: React.ReactNode; }) {
  return (
    <div className="flex flex-wrap gap-5 items-center rounded-lg bg-white p-3 shadow-sm border max-w-xl">
      {props.children}
    </div>
  );
}
