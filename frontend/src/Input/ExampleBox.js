//TODO: Cache the examples.
import styled from "styled-components";
import React, {useState} from "react";
import ClassicUIBox from "../shared/ClassicUIBox";
import Ticket from "./Ticket";

export function ExampleBox(props) {
    const exampleJSONdata = require('./exampleRequests.json')
    const exampleRequests = exampleJSONdata["requests"]
    const [selectedExample, setSelectedExample] = useState('Colonialism')

    function handleExampleClick(requestName){
        setSelectedExample(requestName)
        props.onExampleRequestClick(exampleRequests[requestName]["tickets"])
    }

    return (
        <ClassicUIBox flexDirection={'row'} ref={props.exampleBoxRef}>
            <StyledExampleSelector>
                {Object.keys(exampleRequests).map((requestName) => (
                    <StyledExampleButtonSelect
                        key={requestName}
                        onClick={() => handleExampleClick(requestName)}
                        selected={requestName === selectedExample}
                    >
                        <h1>{requestName}</h1>
                    </StyledExampleButtonSelect>
                ))}
            </StyledExampleSelector>
            <ExampleContext>
                {exampleRequests[selectedExample]}
            </ExampleContext>
        </ClassicUIBox>

    )
}

function ExampleContext(props) {
    console.log(props.children)
    return (
        <ExampleRequest
            request={props.children}
        />
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
    justify-content: space-between;
    align-items: start;
    gap: 50px;
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