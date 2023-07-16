import Head from "next/head";
import "./globals.css";
import { Providers } from "./components/Providers";

export default function RootLayout({
  // Layouts must accept a children prop.
  // This will be populated with nested layouts or pages
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <Head>
        <title>Gallica Context</title>
        <meta
          name="View context surrounding occurrences of words in the French national archive."
          content="Gallica Context"
        />
      </Head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
