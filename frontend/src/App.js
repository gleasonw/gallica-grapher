import React, {useState, useRef} from 'react';
import {v4 as uuidv4} from 'uuid';
import InputUI from "./components/InputUI";
import RunningQueriesUI from "./components/RunningQueriesUI";
import ReactMarkdown from 'react-markdown';
import ResultUI from "./components/ResultUI";
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
    const formRef = useRef(null);

    const header =
        <header className="header">
            <div className="infoAndHomeBar">
                <div
                    className={'gallicaGrapherHome'}
                    onClick={handleHomeClick}
                >
                    Graphing Gallica
                </div>
                <div
                    className="info"
                    onClick={handleInfoClick}
                >
                    <InfoIcon/>
                </div>
            </div>
        </header>

    async function handleInputSubmit(event){
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
        formRef.current.scrollIntoView({behavior: 'smooth'});
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
            <div>
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
                <InputUI
                    requestTickets={tickets}
                    onInputSubmit={handleInputSubmit}
                    onCreateTicketClick={handleCreateTicketClick}
                    onTicketClick={handleTicketClick}
                    onExampleRequestClick={handleExampleRequestClick}
                    formRef={formRef}
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
                    <span>
            Your request returned {numRecords.toLocaleString()} records from Gallica's archive. This number is either
                        greater than my limit, or I don't have enough space for it right now. Try restricting your search to a few periodicals,
            shortening the year range, or using a more precise ngram. Click on Graphing Gallica to return to home.
                    </span>
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