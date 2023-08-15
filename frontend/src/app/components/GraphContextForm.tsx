"use client";

import { useSearchState } from "../composables/useSearchState";
import { InputLabel } from "./InputLabel";
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
  const { terms, selected_term, year, end_year, month } = useSearchState();
  console.log(terms);

  return (
    <>
      <div className={"flex flex-col gap-5 ml-5 mr-5 mt-2"}>
        {translation.gallicagram_plug}
        <div className={"flex wrap gap-10"}>
          <SelectInput
            options={terms?.map((term) => term) ?? []}
            onChange={(value: string) => console.log(value)}
            value={terms?.find((t) => t === selected_term)}
          />
          <ContextFilter
            onClick={() => console.log("clear year")}
            label={year && end_year ? `${year} - ${end_year}` : undefined}
          />
          <ContextFilter
            label={month ? translation.months[month - 1] : undefined}
            onClick={() => console.log("clear month")}
          />
        </div>
      </div>

      <div className={"flex flex-row flex-wrap gap-5 md:gap-10 lg:gap-10"}>
        <InputLabel label={"Année"}>
          <input
            type={"number"}
            className={"border rounded-lg bg-white p-3"}
            value={year || ""}
            onChange={(e) => console.log(e)}
          />
        </InputLabel>
        <InputLabel label={"Mois"}>
          <SelectInput
            options={Array.from(Array(12).keys()).map((i) => String(i))}
            onChange={() => console.log("month!")}
            value={month ? String(month) : undefined}
          />
        </InputLabel>
        <InputLabel label={"Ticket"}>
          <select
            onChange={() => console.log("change selected term")}
            className={"border rounded-lg  bg-white p-3"}
            value={selected_term}
          >
            {terms?.map((term) => (
              <option key={term} value={term}>
                {term}
              </option>
            ))}
          </select>
        </InputLabel>
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
