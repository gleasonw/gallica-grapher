//TODO: Cache the examples.
import styled from "styled-components";
import React, {useState} from "react";
import ClassicUIBox from "../shared/ClassicUIBox";
import Ticket from "./Ticket";
import {descriptions} from "./ExampleDescriptions";

export function ExampleBox(props) {
    const exampleJSONdata = require('./exampleRequests.json')
    const exampleRequests = exampleJSONdata["requests"]
    const [selectedExample, setSelectedExample] = useState('Colonialism')

    return (
        <ClassicUIBox
            flexDirection={'row'}
            ref={props.exampleBoxRef}
            flex={'none'}
            width={'1200px'}
            height={'auto'}
        >
            <StyledExampleSelector>
                {Object.keys(exampleRequests).map((requestName) => (
                    <StyledExampleButtonSelect
                        key={requestName}
                        onClick={() => setSelectedExample(requestName)}
                        selected={requestName === selectedExample}
                    >
                        <h1>{requestName}</h1>
                    </StyledExampleButtonSelect>
                ))}
            </StyledExampleSelector>
            <StyledExampleContext>
                <ExampleRequest request={exampleRequests[selectedExample]}/>
                <StyledContextReader>
                    <div dangerouslySetInnerHTML={{__html: descriptions[selectedExample]}}/>
                </StyledContextReader>
            </StyledExampleContext>
        </ClassicUIBox>

    )
}

function ExampleRequest(props){
    const tickets = props.request["tickets"]
    const numTickets = Object.keys(tickets).length
    return(
            <div className={'exampleRequest'}>
                {Object.keys(tickets).map((ticket, index) => (
                    <Ticket
                        ticket={tickets[ticket]}
                        key={ticket}
                        ticketID={ticket}
                        firstInRow={index === 0}
                        lastInRow={index === numTickets - 1}
                    />
                ))}
            </div>
    )
}

const StyledExampleSelector = styled.div`
    display: flex;
    flex-direction: column;
    align-items: start;
    gap: 10px;
    border-right: 1px solid black;
    padding-right: 20px;
`;
const StyledExampleButtonSelect = styled.button`
    background-color: transparent;
    &:hover{
        ${props => props.selected ? '' : 'background-color: #e0e0e0;'}
    }
    color: ${props => props.selected ? 'black' : '#787878'};
    border: ${props => props.selected ? '1px solid black' : ''};
    border-radius: 5px;
    padding: 5px;
`;

const StyledExampleContext = styled.div`
    display: flex;
    flex-direction: column;
    padding: 20px;
    font-size: 20px;
    gap: 20px;
    `;

const StyledContextReader = styled.div`
    width: calc(100% - 40px);
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
    text-align: justify;
    `;