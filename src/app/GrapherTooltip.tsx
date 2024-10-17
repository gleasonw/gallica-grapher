"use client";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Check, Copy } from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { client } from "@/src/app/utils";
import { forwardRef } from "react";

export const GrapherTooltip = forwardRef(function GrapherTooltip(
  props: {
    content: React.ReactNode;
    trigger: React.ReactNode;
  },
  ref
) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild ref={ref as any}>
          {props.trigger}
        </TooltipTrigger>
        <TooltipContent>{props.content}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
});

export function PageImage(props: { page: number; ark: string; term: string }) {
  const { data, isLoading, isError } = useQuery({
    queryKey: [props.ark, props.page, props.term],
    queryFn: async () =>
      await client.GET("/api/image", { params: { query: props } }),
  });
  if (isLoading) {
    return <div>Chargement...</div>;
  }
  if (isError) {
    return <div>Erreur...</div>;
  }
  return <img src={data?.data?.image} />;
}

export function CopyButton({ text }: { text: string }) {
  const [clicked, setClicked] = useState(false);
  return (
    <GrapherTooltip
      trigger={
        <Button
          variant="ghost"
          className="text-gray-500"
          onClick={async () => {
            setClicked(true);
            await navigator.clipboard.writeText(text);
            setTimeout(() => setClicked(false), 2000);
          }}
        >
          {clicked ? <Check /> : <Copy />}
        </Button>
      }
      content={<div>Copier l'URL de la page</div>}
    />
  );
}
