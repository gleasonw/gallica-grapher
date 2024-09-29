"use client";

import React from "react";
import { createStore } from "zustand";

type ImagePageTag = string & { __tag__: "ImagePageTag" };

type ClientState = {
  shownImages: Set<ImagePageTag>;
  showImageFor: (page: ImagePageTag) => void;
  getImageTag: (page: number, ark: string) => ImagePageTag;
  hideImageFor: (page: ImagePageTag) => void;
};

const occurrenceStore = createStore<ClientState>((set) => ({
  shownImages: new Set(),
  showImageFor: (page: ImagePageTag) =>
    set((state) => ({ shownImages: state.shownImages.add(page) })),
  hideImageFor: (page: ImagePageTag) =>
    set((state) => {
      const newSet = new Set(state.shownImages);
      newSet.delete(page);
      return { shownImages: newSet };
    }),
  getImageTag: (page: number, ark: string) =>
    `${ark}-withImage-${page}` as ImagePageTag,
}));

const OccurrenceContext = React.createContext<ClientState | null>(null);

export function ImageStateProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div>{children}</div>;
}
