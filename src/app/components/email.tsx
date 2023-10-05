"use client";

import React from "react";
import { GallicaButton } from "./design_system/GallicaButton";

export function Email() {
  const [isShown, setIsShown] = React.useState(false);

  return (
    <GallicaButton onClick={() => setIsShown(true)}>
      {isShown ? process.env.NEXT_PUBLIC_EMAIL : "mail (click)"}
    </GallicaButton>
  );
}
