import { AnimatePresence, motion } from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import React from "react";
import { useRouter } from "next/router";

export default function NavBar() {
  const [showSidebar, setShowSidebar] = React.useState(false);
  const [lang, setLang] = React.useState<"fr" | "en">("fr");
  const router = useRouter();
  let currentPage = router.pathname.split("/")[1];
  if (currentPage === "") {
    currentPage = "graph";
  }
  const linkStyle = "p-5 hover:cursor-pointer";
  let homeLinkStyle = linkStyle;
  let exploreLinkStyle = linkStyle;
  let infoLinkStyle = linkStyle;
  const borderBottomFocus = " border-b border-blue-500 border-b-4";
  if (currentPage === "graph") {
    homeLinkStyle += borderBottomFocus;
  } else if (currentPage === "context") {
    exploreLinkStyle += borderBottomFocus;
  } else if (currentPage === "info") {
    infoLinkStyle += borderBottomFocus;
  }

  const styleMap: { [key: string]: string } = {
    graph: homeLinkStyle,
    context: exploreLinkStyle,
    info: infoLinkStyle,
  };

  const links = [
    { name: "Graph", href: "/" },
    { name: "Context", href: "/context" },
    { name: "Info", href: "/info" },
  ];

  return (
    <div className="flex flex-col">
      <div className="flex flex-col sticky top-0 z-50">
        <div
          className={
            "flex flex-row items-center justify-between p-5 border-b-2 bg-white shadow-sm"
          }
        >
          <div className={"flex"}>
            <svg
              focusable="false"
              viewBox="0 0 24 24"
              className="w-10 hover:cursor-pointer hover:bg-zinc-100 rounded-full"
              onClick={() => setShowSidebar(!showSidebar)}
            >
              <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"></path>
            </svg>
            <Link className={"p-5 text-3xl"} href={"/"}>
              Gallica Grapher
            </Link>
            <div className="hidden lg:flex xl:flex items-center">
              {links.map((link) => (
                <Link
                  key={link.name}
                  href={link.href}
                  className={styleMap[link.name.toLowerCase()]}
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </div>
          <div className={"flex flex-row gap-5 align-center justify-center"}>
            <select
              onChange={() => setLang(lang === "fr" ? "en" : "fr")}
              value={lang}
              className={""}
            >
              <option value="fr">Français</option>
              <option value="en">English</option>
            </select>
            <Link
              href={"https://github.com/gleasonw/gallica-grapher"}
              target={"_blank"}
            >
              <Image
                src={"/github.svg"}
                width={40}
                height={40}
                alt={"Github"}
              />
            </Link>
          </div>
        </div>
        <AnimatePresence>
          {showSidebar && (
            <motion.div
              initial={{ x: -1000 }}
              animate={{ x: 0 }}
              exit={{ x: -1000 }}
              transition={{ duration: 0.2 }}
              className={"sticky top-0"}
            >
              <div
                className={
                  "absolute bg-white z-40 flex flex-col gap-1 p-2 h-screen border-r shadow-md"
                }
              >
                {links.map((link) => (
                  <Link
                    key={link.name}
                    href={link.href}
                    className={
                      "p-5 w-60 hover:bg-blue-100 rounded-lg hover:cursor-pointer"
                    }
                  >
                    {link.name}
                  </Link>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
