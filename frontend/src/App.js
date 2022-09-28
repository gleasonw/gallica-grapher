import React, {useRef, useState} from 'react';
import Input from "./Input/Input";
import Info from "./Info";
import RunningQueriesUI from "./Running/RunningQueries";
import ResultUI from "./Result/ResultUI";
import './style.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import InfoIcon from '@mui/icons-material/Info';
import axios from "axios";
import ClassicUIBox from "./shared/ClassicUIBox";
import ImportantButtonWrap from "./shared/ImportantButtonWrap";


function App() {
    const [tickets, setTickets] = useState({});
    const [requestID, setRequestID] = useState(null);
    const [progressID, setProgressID] = useState(null);
    const [currentPage, setCurrentPage] = useState('input');
    const [numRecords, setNumRecords] = useState(0);
    const requestBoxRef = useRef(null);
    const pages = {
        'input':
            <Input
                tickets={tickets}
                onLoadedSubmit={handleLoadedSubmit}
                onUnloadedSubmit={handleUnloadedSubmit}
                onCreateTicketClick={handleCreateTicketClick}
                onTicketClick={handleTicketClick}
                onExampleRequestClick={handleExampleRequestClick}
                requestBoxRef={requestBoxRef}
            />,
        'running':
            <RunningQueriesUI
                tickets={tickets}
                progressID={progressID}
                requestID={requestID}
                onFinish={() => setCurrentPage('result')}
                onTooManyRecords={handleTooManyRecords}
                onNoRecords={() => setCurrentPage('noRecords')}
                onCancelRequest={handleResetValuesAndGoHome}
                onBackendError={() => setCurrentPage('backendError')}
            />,
        'result':
            <ResultUI
                tickets={tickets}
                requestID={requestID}
                onHomeClick={handleResetValuesAndGoHome}
            />,
        'info':
            <Info/>,
        'tooManyRecords':
            <ClassicUIBox width={'calc(100% - 100px)'} height={'auto'}>
                <h1>Your curiosity exceeds my capacity.</h1>
                <br/>
                <h3>{numRecords.toLocaleString()} records in your request.</h3>
                <section>
                    <br/>
                    <p>This number is either greater than my limit, or I don't have enough space for it right now.
                        Try restricting your search to a few periodicals, shortening the year range, or using a more
                        precise term. </p>
                    <br/>
                </section>
                <ImportantButtonWrap
                    onClick={handleResetValuesAndGoHome}
                    aria-label="Home page button"
                    children={'Make a new request'}
                />
            </ClassicUIBox>,
        'noRecords':
            <ClassicUIBox width={'calc(100% - 100px)'} height={'auto'}>
                <h1>No records found. </h1>
                <p>Try adjusting your year range or periodical selection. Some publish only a few times in a year and
                    don't have much text available. </p>
                <p>Adjusting your search term might help too, although Gallica is usually good at finding similar
                    spellings. </p>
                <ImportantButtonWrap
                    onClick={handleResetValuesAndGoHome}
                    aria-label="Home page button"
                    children={'Make a new request'}
                />
            </ClassicUIBox>,
        'backendError':
            <ClassicUIBox width={'calc(100% - 100px)'} height={'auto'}>
                <h1>Something went wrong. My fault. </h1>
                <p>Rest assured our very best engineer will soon right his wrongs.</p>
                <p>Please try again later!</p>
            </ClassicUIBox>
    }

    function handleLoadedSubmit(ticket) {
        const updatedTickets = getUpdatedTickets(ticket);
        void initRequest(updatedTickets);
    }

    function getUpdatedTickets(ticket) {
        const newTicketID = Object.keys(tickets).length;
        return {
            ...tickets,
            [newTicketID]: ticket
        };
    }

    function handleUnloadedSubmit() {
        void initRequest(tickets);
    }

    async function initRequest(tickets) {
        setCurrentPage('running');
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
        const progressID = JSON.parse(request.response)["taskid"];
        const requestID = JSON.parse(request.response)["requestid"];
        if (progressID === null) {
            setCurrentPage('backendError');
        }
        setProgressID(progressID);
        setRequestID(requestID);
    }

    function handleCreateTicketClick(items) {
        const updatedTickets = getUpdatedTickets(items);
        setTickets(updatedTickets);
    }

    function handleTicketClick(ticketID) {
        let updatedTickets = {...tickets}
        delete updatedTickets[ticketID];
        setTickets(updatedTickets)
    }

    function handleExampleRequestClick(example) {
        const nameToId = {
            "Colors": -1,
            "Arts": -2,
            "Pastries": -3,
            "Scandal": -4,
            "Colonialism": -5,
            "Capitals": -6,
            "Far West": -7
        }
        const [id, tickets] = Object.entries(example)[0];
        const ticketData = tickets['tickets'];
        const requestWithUniqueTicketIDs = {}
        Object.keys(ticketData).map((ticketID, index) => (
            requestWithUniqueTicketIDs[index] = ticketData[ticketID]
        ))
        setTickets(requestWithUniqueTicketIDs);
        setRequestID(nameToId[id])
        setCurrentPage('result')
    }

    function handleTooManyRecords(numRecords) {
        setNumRecords(numRecords);
        setCurrentPage('tooManyRecords');
    }

    function handleResetValuesAndGoHome() {
        setCurrentPage('input');
        setTickets({});
        setRequestID(null);
        setProgressID(null);
        setNumRecords(0);
    }

    return (
        <div className="App">
            <Header
                onHomeClick={handleResetValuesAndGoHome}
                onInfoClick={() => setCurrentPage('info')}
            />
            {pages[currentPage]}
        </div>
    );
}

function Header(props) {
    return (
        <header className="header">
            <div className="infoAndHomeBar">
                <button
                    className={'gallicaGrapherHome'}
                    onClick={props.onHomeClick}
                    aria-label="Home page button"
                >
                    Graphing Gallica
                </button>
                <button
                    className="info"
                    onClick={props.onInfoClick}
                    aria-label="Information page button"
                >
                    <InfoIcon/>
                </button>
            </div>
        </header>
    )
}

export default App;