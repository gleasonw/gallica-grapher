import "./globals.css";
import NavBar from "./components/NavBar";
import { Analytics } from "@vercel/analytics/react";

export default function RootLayout({
  // Layouts must accept a children prop.
  // This will be populated with nested layouts or pages
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <NavBar />
        <Analytics />
        {children}
      </body>
    </html>
  );
}
