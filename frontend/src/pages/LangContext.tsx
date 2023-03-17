import React, { createContext } from "react";

// export const getStaticProps: GetStaticProps<{
//   initRecords: GallicaResponse;
//   initSeries: GraphData[];
// }> = async () => {
//   const records = await fetchContext(0, {
//     terms: initTickets[0].terms,
//     limit: 10,
//     source: "periodical",
//   });
//   const initSeries = await Promise.all(
//     initTickets.map((ticket) => {
//       return getTicketData(ticket.id, ticket.backend_source, "year", 0);
//     })
//   );
//   return {
//     props: {
//       initRecords: records,
//       initSeries: initSeries,
//     },
//   };
// };

export const LangContext = createContext<{
  lang: "fr" | "en";
  setLang: React.Dispatch<React.SetStateAction<"fr" | "en">>;
}>({ lang: "fr", setLang: () => { } });
export const strings = {
  fr: {
    title: "The Gallica Grapher",
    description: "Explorez les occurrences de mots dans des périodiques Gallica.",
    linkTerm: "Terme de proximité",
    linkDistance: "Distance de proximité",
  },
  en: {
    title: "The Gallica Grapher",
    description: "Explore word occurrences in archived Gallica periodicals.",
    linkTerm: "Link term",
    linkDistance: "Link distance",
  },
};
