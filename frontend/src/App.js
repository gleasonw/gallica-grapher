import React, {useState} from 'react';
import {v4 as uuidv4} from 'uuid';
import Input from "./Input/Input";
import RunningQueriesUI from "./Running/RunningQueries";
import ResultUI from "./Result/ResultUI";
import './style.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import axios from "axios";
import InfoIcon from '@mui/icons-material/Info';


function App() {
    const [tickets, setTickets] = useState([]);
    const [idTickets, setIDTickets] = useState({});
    const [requestID, setRequestID] = useState('');
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

    async function handleInputSubmit(event){
        console.log(tickets)
        event.preventDefault();
        const ticksWithIDS = generateTicketIDs();
        const {request} = await axios.post('/api/init', {
            tickets: ticksWithIDS
        })
        const taskID = JSON.parse(request.response)["taskid"];
        setIDTickets(ticksWithIDS);
        setRequestID(taskID);
        setGettingInput(false);
        setRunningQueries(true);
    }

    function handleCreateTicketClick(items){
        createTicketFromInput(items)
    }

    function handleTicketClick(index){
        deleteTicketAtIndex(index);
    }

    function handleExampleRequestClick(request){
        window.scrollTo(0, 0);
        setTickets(request);
    }

    function generateTicketIDs(){
        let ticketsWithID = {};
        for (let i = 0; i < tickets.length; i++){
            let id = uuidv4()
            ticketsWithID[id] = tickets[i]
        }
        return ticketsWithID
    }

    function createTicketFromInput(items){
        if(items.terms.length > 0){
            let updatedTickets = tickets.slice();
            updatedTickets.push(items);
            setTickets(updatedTickets)
        }

    }

    function deleteTicketAtIndex(index){
        const updatedTickets = tickets.slice()
        updatedTickets.splice(index, 1)
        setTickets(updatedTickets)
    }

    function handleTicketFinish(){
        setRunningQueries(false);
    }

    function handleHomeClick(){
        setInfoPage(false)
        setGettingInput(true);
        setRunningQueries(false);
        setTickets([]);
        setIDTickets({});
        setRequestID('');
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
                    requestTickets={tickets}
                    onInputSubmit={handleInputSubmit}
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
                    tickets={idTickets}
                    onFinish={handleTicketFinish}
                    requestID={requestID}
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
                <ResultUI
                    tickets={idTickets}
                />
            </div>
          )
    }
}



export default App;