"use client";

import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import React from "react";

export function TermSearchInput() {
  const [searchTerm, setSearchTerm] = React.useState("");
  const router = useRouter();

  return (
    <>
      <Input
        className="w-full pl-10 pr-4 py-6 text-lg shadow-lg"
        placeholder="Search for terms (comma-separated)..."
        value={searchTerm}
        onChange={(e) => {
          setSearchTerm(e.target.value);
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            router.push(`/?term=${searchTerm}`);
          }
        }}
      />
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
    </>
  );
}
