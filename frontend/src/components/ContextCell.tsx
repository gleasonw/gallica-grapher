import React from "react";
import { GallicaRecord } from "../server/routers/_app";
import { Context } from "./Context";
import { RevealButton } from "./RevealButton";

export const ContextCell: React.FC<{ record: GallicaRecord }> = ({
  record,
}) => {
  const [showContext, setShowContext] = React.useState(false);

  React.useEffect(() => {
    setShowContext(false);
  }, [record]);

  return (
    <td className={"p-3"}>
      {showContext ? (
        <Context
          onHideContextClick={() => setShowContext(false)}
          url={record.url}
          term={record.term}
        />
      ) : (
        <RevealButton label={"View context"} onClick={() => setShowContext(true)} />
      )}
    </td>
  );
};
