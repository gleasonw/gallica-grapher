"use client";

import { InputLabel } from "./InputLabel";
import { QueryPagination } from "./QueryPagination";
import { SelectInput } from "./SelectInput";

const gallica_plug = (
  <a
    href="https://shiny.ens-paris-saclay.fr/app/gallicagram"
    target="_blank"
    rel="noreferrer"
    className="text-blue-500 underline"
  >
    Gallicagram
  </a>
);

const strings = {
  fr: {
    title: "The Gallica Grapher",
    description:
      "Explorez les occurrences de mots dans des périodiques Gallica.",
    linkTerm: "Terme de proximité",
    linkDistance: "Distance de proximité",
    zoom_out: "Zoomer à l'échelle originale",
    gallicagram_plug: (
      <>
        <p>
          Données de charte fournies par {gallica_plug}, un projet de Benjamin
          Azoulay et Benoît de Courson.
        </p>
      </>
    ),
    grouping: "Résolution",
    smoothing: "Lissage",
    months: [
      "Janvier",
      "Février",
      "Mars",
      "Avril",
      "Mai",
      "Juin",
      "Juillet",
      "Août",
      "Septembre",
      "Octobre",
      "Novembre",
      "Décembre",
    ],
  },
  en: {
    title: "The Gallica Grapher",
    description: "Explore word occurrences in archived Gallica periodicals.",
    linkTerm: "Link term",
    linkDistance: "Link distance",
    zoom_out: "Zoom out",
    gallicagram_plug: (
      <>
        <p>
          Chart data provided by {gallica_plug}, a project by Benjamin Azoulay
          and Benoît de Courson.
        </p>
      </>
    ),
    grouping: "Grouping",
    smoothing: "Smoothing",
    months: [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ],
  },
};

export default function GraphContextForm({
  numResults,
}: {
  numResults?: number;
}) {
  const translation = strings["fr"];
  return (
    <>
      <div className={"flex flex-col gap-5 ml-5 mr-5 mt-2"}>
        {translation.gallicagram_plug}
        <div className={"flex wrap gap-10"}>
          <SelectInput
            options={tickets?.map((ticket) => ticket.terms[0]) ?? []}
            onChange={(value: string) =>
              setSelectedTicket(
                tickets?.filter((t) => t.terms[0] === value)[0].id
              )
            }
            value={
              tickets?.filter((t) => t.id === selectedTicket)?.[0]?.terms[0]
            }
          />
          <ContextFilter
            label={
              searchFrom && searchTo ? `${searchFrom} - ${searchTo}` : undefined
            }
          />
          <ContextFilter
            label={month ? translation.months[month - 1] : undefined}
            onClick={() => setMonth(undefined)}
          />
        </div>
      </div>

      <div className={"flex flex-row flex-wrap gap-5 md:gap-10 lg:gap-10"}>
        <InputLabel label={lang === "fr" ? "Année" : "Year"}>
          <input
            type={"number"}
            className={"border rounded-lg bg-white p-3"}
            value={searchFrom || ""}
            onChange={(e) => {
              setSearchFrom(parseInt(e.target.value));
              if (searchTo && parseInt(e.target.value) > searchTo) {
                setSearchTo(parseInt(e.target.value));
              }
            }}
          />
        </InputLabel>
        <InputLabel label={lang === "fr" ? "Mois" : "Month"}>
          <SelectInput
            options={Array.from(Array(12).keys()).map((i) => String(i))}
            onChange={(value) => setMonth(parseInt(value))}
            value={month ? String(month) : undefined}
          />
        </InputLabel>
        <InputLabel label={"Ticket"}>
          <select
            onChange={(e) => {
              setSelectedTicket(parseInt(e.target.value));
            }}
            className={"border rounded-lg  bg-white p-3"}
            value={selectedTicket || ""}
          >
            {tickets?.map((ticket) => (
              <option key={ticket.id} value={ticket.id}>
                {ticket.terms}
              </option>
            ))}
          </select>
        </InputLabel>
        <QueryPagination numResults={numResults} />
      </div>
    </>
  );
}

function ContextFilter({
  label,
  onClick,
}: {
  label: any;
  onClick: () => void;
}) {
  if (!label) {
    return <></>;
  }
  return (
    <div className={"flex flex-row gap-2"}>
      <button
        className={
          "flex flex-row gap-5 items-center border shadow-md rounded-md p-3 hover:bg-zinc-100"
        }
        onClick={onClick}
      >
        <div>{label}</div>
        <div>X</div>
      </button>
    </div>
  );
}
