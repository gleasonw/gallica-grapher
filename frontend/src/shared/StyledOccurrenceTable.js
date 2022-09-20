import styled from "styled-components";

export const StyledOccurrenceTable = styled.table`
    border-collapse: collapse;
    table-layout: fixed;
    td{
        padding: 5px;
    }
    td:hover{
        overflow: visible;
        white-space: normal;
        height: auto;
    }
    tr:nth-child(even){
        background-color: #f2f2f2;
    }
    min-width: 100%;
`;