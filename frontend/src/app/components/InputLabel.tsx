import React, { ReactNode } from "react";


export const InputLabel: React.FC<{ label: string; children: ReactNode; }> = ({
  label, children,
}) => {
  return (
    <div className={"flex flex-col"}>
      <label className={"text-md"}>{label}</label>
      {children}
    </div>
  );
};
