"use client";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { usePageState } from "@/src/app/PageContextClientStateProvider";
import { Check, Copy, Image } from "lucide-react";
import { useState } from "react";
import { observer } from "mobx-react-lite";
import { useQuery } from "@tanstack/react-query";
import { client } from "@/src/app/utils";

export function GrapherTooltip({
  trigger,
  content,
}: {
  trigger: React.ReactElement;
  content: React.ReactElement;
}) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{trigger}</TooltipTrigger>
        <TooltipContent>{content}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export const PageImageGate = observer(function PageImageGate({
  children,
}: {
  children: React.ReactNode;
}) {
  const pageState = usePageState();
  if (!pageState.isImageShowing) {
    return null;
  }
  return children;
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

export const ShowImageButton = observer(function ShowImageButton() {
  const pageState = usePageState();
  return (
    <GrapherTooltip
      trigger={
        <Button
          className="ml-auto text-gray-500"
          variant="ghost"
          onClick={() => pageState.showImage()}
        >
          <Image />
        </Button>
      }
      content={<div>Charger l'image de la page</div>}
    />
  );
});

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
