"use client";

import React, { useContext, useMemo } from "react";
import { makeAutoObservable } from "mobx";

class PageContextState {
  isImageShowing = false;
  constructor() {
    makeAutoObservable(this);
  }

  showImage = () => {
    this.isImageShowing = true;
  };
}

const PageStateContext = React.createContext<PageContextState | null>(null);

export function usePageState() {
  const pageState = useContext(PageStateContext);
  if (!pageState) {
    throw new Error("usePageState not called under context");
  }
  return pageState;
}

export function PageContextClientStateProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const store = useMemo(() => new PageContextState(), []);
  return (
    <PageStateContext.Provider value={store}>
      {children}
    </PageStateContext.Provider>
  );
}
