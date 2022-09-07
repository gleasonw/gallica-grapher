import React, {useState} from 'react';
import {v4 as uuidv4} from 'uuid';
import Input from "./Input/Input";
import RunningQueriesUI from "./Running/RunningQueries";
import ResultUI from "./Result/ResultUI";
import './style.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import InfoIcon from '@mui/icons-material/Info';
import axios from "axios";


function App() {
    const [tickets, setTickets] = useState({});
    const [requestID, setRequestID] = useState(null);
    const [gettingInput, setGettingInput] = useState(true);
    const [runningQueries, setRunningQueries] = useState(false);
    const [infoPage, setInfoPage] = useState(false);
    const [tooManyRecordsWarning, setTooManyRecordsWarning] = useState(false);
    const [numRecords, setNumRecords] = useState(0);

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

    async function handleTicketSubmit(ticket){
        const newTicketID = uuidv4();
        const updatedTickets = {
            ...tickets,
            [newTicketID]: ticket
        };
        const requestID = await initRequest(updatedTickets);
        setTickets(updatedTickets);
        setRequestID(requestID);
        setRunningQueries(true);
        setGettingInput(false);
    }

    async function initRequest(allUserTickets) {
        const {request} = await axios.post('/api/init', {
            tickets: allUserTickets
        })
        return JSON.parse(request.response)["taskid"];
    }

    function handleCreateTicketClick(items){

        function createTicketFromInput(items){
            const ticketID = uuidv4();
            let updatedTickets = {
                ...tickets,
                [ticketID]: items
            };
            setTickets(updatedTickets);
        }
        createTicketFromInput(items)
    }

    function handleTicketClick(ticketID){

        function deleteTicket(key){
            let updatedTickets = {...tickets}
            delete updatedTickets[key];
            setTickets(updatedTickets)
        }
        deleteTicket(ticketID);
    }

    function handleExampleRequestClick(request){
        setTickets(request);
    }

    function handleTicketFinish(){
        setRunningQueries(false);
    }

    function handleHomeClick(){
        setInfoPage(false)
        setGettingInput(true);
        setRunningQueries(false);
        setTickets({});
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
                <div className={'infoText'}>
                    This is a graphing tool.
                </div>
            </div>
        )
    }else if(gettingInput){
        return (
            <div className="App">
                {header}
                <Input
                    tickets={tickets}
                    onTicketSubmit={handleTicketSubmit}
                    onCreateTicketClick={handleCreateTicketClick}
                    onTicketClick={handleTicketClick}
                    onExampleRequestClick={handleExampleRequestClick}
                />
            </div>
        )
    }else if(runningQueries){
        return (
            <div className="App">
                {header}
                <RunningQueriesUI
                    tickets={tickets}
                    taskID={requestID}
                    onFinish={handleTicketFinish}
                    onTooManyRecords={handleTooManyRecords}
                />
            </div>
        )
    }else if(tooManyRecordsWarning){
        return (
            <div className="App">
                {header}
                <div className={'tooManyRecordsWarningBox'}>
                    <h1>Your curiosity exceeds my capacity.</h1>
                    <section>
            Your request returned {numRecords.toLocaleString()} records from Gallica's archive. This number is either
                        greater than my limit, or I don't have enough space for it right now. Try restricting your search to a few periodicals,
            shortening the year range, or using a more precise term. Click on Graphing Gallica to return to home.
                    </section>
                </div>
            </div>
        )
    }else{
        return (
            <div className="App">
                {header}
                <ResultUI tickets={tickets}/>
            </div>
          )
    }
}



export default App;