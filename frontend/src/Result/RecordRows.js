import OCRText from "./OCRText";
import React from "react";
import styled from 'styled-components';

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
                    <td>
                        {(year && month && day) && `${year}/${month}/${day}`}
                        {(year && month && !day) && `${year}/${month}`}
                        {(year && !month && !day) && `${year}`}
                    </td>
                    <td>{periodical}</td>
                    <td>{term}</td>
                    <td>
                        <a
                            href={gallicaLink}
                            target='_blank'
                            rel='noopener noreferrer'
                        >
                            {gallicaLink}</a>
                    </td>
                    <StyledOCRTD>
                        <OCRText
                            term={term}
                            arkCode={arkCode}
                        />
                    </StyledOCRTD>
                </tr>
            )
        })
    )
}

const StyledOCRTD = styled.td`
    width: 600px;
    `;