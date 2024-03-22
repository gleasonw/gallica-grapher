import React from "react";
import { ContextInputForm } from "../components/ContextInputForm";
import {
  GallicaRecord,
  fetchContext,
  fetchFullText,
} from "../components/fetchContext";
import { getSearchStateFromURL } from "../utils/searchState";
import { LoadingProvider } from "../components/LoadingProvider";
import ContextViewer from "../components/ContextViewer";
import { ImageSnippet } from "../components/ImageSnippet";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/design_system/card";
import { Sparkles } from "lucide-react";
import { Button } from "../components/design_system/button";
import OpenAI from "openai";
import fs from "fs";

const openai = new OpenAI();

export default async function Page({
  searchParams,
}: {
  searchParams: Record<string, any>;
}) {
  const params = getSearchStateFromURL(searchParams);
  const contextParams = {
    ...params,
    terms: params?.terms ?? [],
    all_context: true,
  };
  const data = params.terms?.some((term) => !!term)
    ? await fetchContext(contextParams)
    : { records: [], num_results: 0 };

  const maybeNumberResults = data.num_results;
  let numResults = 0;
  if (!isNaN(maybeNumberResults) && maybeNumberResults > 0) {
    numResults = maybeNumberResults;
  }

  function getPageNumberFromParams(ark: string) {
    if (Object.keys(searchParams)?.includes(`arkPage${ark}`)) {
      return searchParams[`arkPage${ark}`];
    }
  }

  return (
    <LoadingProvider>
      <ContextInputForm params={contextParams} num_results={numResults}>
        <div className={"flex flex-col gap-20 md:m-5"}>
          {data.records?.map((record, index) => (
            <Card key={`${record.ark}-${record.terms}-${index}`}>
              <h1 className="flex justify-between">
                <CardHeader>
                  <CardTitle>{record.paper_title}</CardTitle>
                  <CardDescription>{record.date}</CardDescription>
                </CardHeader>
                <DocumentConversation ark={record.ark} />
              </h1>
              <ContextViewer
                data={record.context}
                ark={record.ark}
                image={
                  <ImageSnippet
                    ark={record.ark}
                    term={record.terms[0]}
                    pageNumber={
                      getPageNumberFromParams(record.ark) ??
                      record.context[0].page_num
                    }
                  />
                }
              />
            </Card>
          ))}
        </div>
      </ContextInputForm>
    </LoadingProvider>
  );
}

function DocumentConversation({ ark }: { ark: string }) {
  async function initiateConversation() {
    "use server";
    const fullText = await fetchFullText({ ark });

    // create json file from fullText
    const jsonString = JSON.stringify(fullText);
    fs.writeFileSync("output.json", jsonString, "utf8");
    const file = await openai.files.create({
      file: fs.createReadStream("output.json"),
      purpose: "assistants",
    });
    const assistant = await openai.beta.assistants.create({
      name: "Newspaper analyst",
      instructions:
        "You are a personal newspaper analyst. Read the text to draw conclusions and highlight important citations, with page numbers.",
      model: "gpt-4-1106-preview",
      file_ids: [file.id],
      tools: [{ type: "retrieval" }],
    });
    const thread = await openai.beta.threads.create({
      messages: [
        { content: "What can you tell me about this newspaper?", role: "user" },
      ],
    });
    const run = await openai.beta.threads.runs.create(thread.id, {
      assistant_id: assistant.id,
    });
    while (true) {
      console.log("waiting for run to complete");
      const polledRun = await openai.beta.threads.runs.retrieve(
        thread.id,
        run.id
      );
      if (polledRun.status === "completed") {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    const messages = await openai.beta.threads.messages.list(thread.id);
  }

  return (
    <form action={initiateConversation}>
      <Button variant="ghost">
        <Sparkles />
      </Button>
    </form>
  );
}
