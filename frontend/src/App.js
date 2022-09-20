import React, {useState, useRef} from 'react';
import {v4 as uuidv4} from 'uuid';
import Input from "./Input/Input";
import Info from "./Info";
import RunningQueriesUI from "./Running/RunningQueries";
import ResultUI from "./Result/ResultUI";
import './style.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import InfoIcon from '@mui/icons-material/Info';
import axios from "axios";
import ClassicUIBox from "./shared/ClassicUIBox";


function App() {
    const [tickets, setTickets] = useState({});
    const [requestID, setRequestID] = useState(null);
    const [gettingInput, setGettingInput] = useState(true);
    const [runningQueries, setRunningQueries] = useState(false);
    const [infoPage, setInfoPage] = useState(false);
    const [tooManyRecordsWarning, setTooManyRecordsWarning] = useState(false);
    const [numRecords, setNumRecords] = useState(0);
    const requestBoxRef = useRef(null);

    const header =
        <header className="header">
            <div className="infoAndHomeBar">
                <button
                    className={'gallicaGrapherHome'}
                    onClick={handleHomeClick}
                    aria-label="Home page button"
                >
                    Graphing Gallica
                </button>
                <button
                    className="info"
                    onClick={handleInfoClick}
                    aria-label="Information page button"
                >
                    <InfoIcon/>
                </button>
            </div>
        </header>

    function handleLoadedSubmit(ticket){
        const newTicketID = uuidv4();
        const updatedTickets = {
            ...tickets,
            [newTicketID]: ticket
        };
        void initRequest(updatedTickets);
    }

    function handleUnloadedSubmit(){
        void initRequest(tickets);
    }

    async function initRequest(tickets){
        setRunningQueries(true);
        setGettingInput(false);
        setTickets(tickets);
        const ticketsWithJustCodes = {}
        Object.keys(tickets).map((ticketID) => (
            ticketsWithJustCodes[ticketID] = {
                    terms: tickets[ticketID].terms,
                    codes: tickets[ticketID].papersAndCodes.map(
                        (paperAndCode) => (paperAndCode.code)),
                    dateRange: tickets[ticketID].dateRange
            }
        ))
        const {request} = await axios.post('/api/init', {
            tickets: ticketsWithJustCodes
        })
        const requestID = JSON.parse(request.response)["taskid"];
        setRequestID(requestID);
    }

    function handleCreateTicketClick(items){
        const ticketID = uuidv4();
        let updatedTickets = {
            ...tickets,
            [ticketID]: items
        };
        setTickets(updatedTickets);
    }

    function handleTicketClick(ticketID){
        let updatedTickets = {...tickets}
        delete updatedTickets[ticketID];
        setTickets(updatedTickets)
    }

    function handleExampleRequestClick(request){
        requestBoxRef.current.scrollIntoView({behavior: 'smooth'});
        const requestWithUniqueTicketIDs = {}
        Object.keys(request).map((ticketID) => (
            requestWithUniqueTicketIDs[uuidv4()] = request[ticketID]
        ))
        setTickets(requestWithUniqueTicketIDs);
    }

    function handleTicketFinish(){
        setRunningQueries(false);
    }

    function handleHomeClick(){
        setInfoPage(false)
        setGettingInput(true);
        setRunningQueries(false);
        setTickets({});
        setRequestID(null);
        setTooManyRecordsWarning(false);
        setNumRecords(0);
    }

    function handleTooManyRecords(numRecords){
        setRunningQueries(false);
        setTooManyRecordsWarning(true);
        setNumRecords(numRecords);
    }

    function handleInfoClick(){
        setInfoPage(true);
    }

    if(infoPage) {
        return(
            <div className="App">
                {header}
                <Info/>
            </div>
        )
    }else if(gettingInput){
        return (
            <div className="App">
                {header}
                <Input
                    tickets={tickets}
                    onLoadedSubmit={handleLoadedSubmit}
                    onUnloadedSubmit={handleUnloadedSubmit}
                    onCreateTicketClick={handleCreateTicketClick}
                    onTicketClick={handleTicketClick}
                    onExampleRequestClick={handleExampleRequestClick}
                    requestBoxRef={requestBoxRef}
                />
            </div>
        )
    }else if(runningQueries){
        return (
            <div className="App">
                {header}
                <RunningQueriesUI
                    tickets={tickets}
                    requestID={requestID}
                    onFinish={handleTicketFinish}
                    onTooManyRecords={handleTooManyRecords}
                />
            </div>
        )
    }else if(tooManyRecordsWarning){
        return (
            <div className="App">
                {header}
                <ClassicUIBox>
                    <h1>Your curiosity exceeds my capacity.</h1>
                    <br/>
                    <h3>{numRecords.toLocaleString()} records in your request.</h3>
                    <section>
            This number is either greater than my limit, or I don't have enough space for it right now. Try restricting your search to a few periodicals,
            shortening the year range, or using a more precise term. Click on Graphing Gallica to return to home.
                    </section>
                </ClassicUIBox>
            </div>
        )
    }else{
        return (
            <div className="App">
                {header}
                <ResultUI
                    tickets={tickets}
                    requestID={requestID}
                />
            </div>
          )
    }
}



export default App;