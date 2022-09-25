import OCRTextBubble from "./OCRTextBubble";
import React from "react";

export function RecordRows(props) {
    return (
        props.rows.map((record, index) => {
            let term = record[0];
            let periodical = record[1];
            let year = record[2];
            let month = record[3];
            let day = record[4];
            let gallicaLink = record[5];
            let arkCode = gallicaLink.split('/').pop();
            return (
                <tr key={index}>
                    <td>{index + props.offset + 1}</td>
                    <td>{term}</td>
                    <td>{periodical}</td>
                    <td>
                        {(year && month && day) && `${year}/${month}/${day}`}
                        {(year && month && !day) && `${year}/${month}`}
                        {(year && !month && !day) && `${year}`}
                    </td>
                    <td>
                        <a
                            href={gallicaLink}
                            target='_blank'
                            rel='noopener noreferrer'
                        >
                            {gallicaLink}</a>
                    </td>
                    <td>
                        <OCRTextBubble
                            term={term}
                            arkCode={arkCode}
                        />
                    </td>
                </tr>
            )
        })
    )
}