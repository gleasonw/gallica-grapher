import OCRText from "./OCRText";
import React from "react";
import styled from 'styled-components';

export function RecordRows(props) {
    console.log(props.rows);
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
                    <td>
                        {(year && month && day) && `${year}/${month}/${day}`}
                        {(year && month && !day) && `${year}/${month}`}
                        {(year && !month && !day) && `${year}`}
                    </td>
                    {!props.compact && <td>{periodical}</td>}
                    <td>{term}</td>
                    <StyledOCRTD>
                        <OCRText
                            term={term}
                            arkCode={arkCode}
                        />
                    </StyledOCRTD>
                    {!props.compact &&
                        <td>
                            <a
                                href={gallicaLink}
                                target='_blank'
                                rel='noopener noreferrer'
                            >
                                {gallicaLink}</a>
                        </td>
                    }
                </tr>
            )
        })
    )
}

const StyledOCRTD = styled.td`
    `;