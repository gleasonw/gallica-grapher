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
    const [selectedSearchType, setSelectedSearchType] = useState(0);
    const [startYear, setStartYear] = useState(1880);
    const [endYear, setEndYear] = useState(1930);
    const [requestID, setRequestID] = useState(null);
    const [progressID, setProgressID] = useState(null);
    const [currentPage, setCurrentPage] = useState('input');
    const [numRecords, setNumRecords] = useState(0);
    const [mismatchedDataOrigin, setMismatchedDataOrigin] = useState([false, false]);
    const requestBoxRef = useRef(null);
    const pages = {
        'input':
            <Input
                tickets={tickets}
                onLoadedSubmit={(ticket) => initRequest(getUpdatedTickets(ticket))}
                onUnloadedSubmit={() => initRequest(tickets)}
                onCreateTicketClick={handleCreateTicketClick}
                onTicketClick={handleTicketClick}
                onExampleRequestClick={handleExampleRequestClick}
                requestBoxRef={requestBoxRef}
                selectedSearchType={selectedSearchType}
                startYear={startYear}
                endYear={endYear}
                onStartYearChange={(year) => setStartYear(year)}
                onEndYearChange={(year) => setEndYear(year)}
                onSearchTypeChange={(i) => setSelectedSearchType(i)}
                mismatchedDataOrigin={mismatchedDataOrigin}
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
                onBackendGroupingChange={handleBackendGroupingChange}
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
                    <p>I can't retrieve all these records for you. There are just too many of them. Try
                        running the same request, but group by year. I don't have to pull as many records from Paris for
                        that.</p>
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

    function getUpdatedTickets(ticket) {
        const newTicketID = Object.keys(tickets).length;
        const dataFromPyllica = ticket.papersAndCodes.length === 0;
        const ticketsDontMatch = Object.values(tickets).some(t => t.dataFromPyllica !== dataFromPyllica);
        if (ticketsDontMatch) {
            alert('Searches over specific periodicals are, for now, not comparable with searches over all periodicals. Mismatching tickets are highlighted in red.')
            setMismatchedDataOrigin([true, dataFromPyllica]);
            return tickets;
        } else {
            setMismatchedDataOrigin([false, dataFromPyllica]);
        }
        return {
            ...tickets,
            [newTicketID]: {
                ...ticket,
                dataFromPyllica: dataFromPyllica,
            }
        };
    }

    function handleBackendGroupingChange(ticketID) {
        const updatedTickets = {
            ...tickets,
            [ticketID]: {
                ...tickets[ticketID],
                grouping: 'all'
            }
        }
        setTickets(updatedTickets);
    }

    async function initRequest(tickets) {
        const completedTickets = addSearchTypeToTickets(tickets);
        const ticketsWithPaperNamesRemoved = removePaperNamesFromTickets(completedTickets);
        //flatten tickets, make index ticketid for each ticket
        const ticketsArray = Object.entries(ticketsWithPaperNamesRemoved).map(([id, ticket]) => (
            {id, ...ticket, start_date: ticket.startDate, end_date: ticket.endDate}
        ));
        const {request} = await axios.post(`${process.env.REACT_APP_API_URL}/api/init`, ticketsArray);
        const progressID = JSON.parse(request.response)["taskid"];
        const requestID = JSON.parse(request.response)["requestid"];
        if (progressID === null) {
            setCurrentPage('backendError');
        }
        setProgressID(progressID);
        setRequestID(requestID);
        setTickets(completedTickets);
        setCurrentPage('running');
    }

    function addSearchTypeToTickets(someTickets) {
        const searchTypes = ['year', 'month', 'all']
        const searchType = searchTypes[selectedSearchType];
        const ticketsWithSearchType = {}
        Object.keys(someTickets).forEach((ticketID) => {
            ticketsWithSearchType[ticketID] = {
                ...someTickets[ticketID],
                grouping: searchType
            }
        })
        return ticketsWithSearchType;
    }

    function removePaperNamesFromTickets(someTickets) {
        const ticketsWithPaperNamesRemoved = {}
        Object.keys(someTickets).map((ticketID) => (
            ticketsWithPaperNamesRemoved[ticketID] = {
                ...someTickets[ticketID],
                codes: someTickets[ticketID].papersAndCodes.map(
                    (paperAndCode) => (paperAndCode.code))
            }
        ))
        delete ticketsWithPaperNamesRemoved['papersAndCodes'];
        return ticketsWithPaperNamesRemoved;
    }

    function handleCreateTicketClick(items) {
        const updatedTickets = getUpdatedTickets(items);
        setTickets(updatedTickets);
    }

    function handleTicketClick(ticketID) {
        let updatedTickets = {...tickets}
        delete updatedTickets[ticketID];
        const renumberedTickets = {};
        Object.keys(updatedTickets).map((oldTicketID, index) => (
            renumberedTickets[index] = updatedTickets[oldTicketID]
        ));
        setTickets(renumberedTickets);
    }

    function handleExampleRequestClick(example) {
        const nameToId = {
            "Colors": -1,
            "Arts": -2,
            "Scandal": -4,
            "Colonialism": -5,
            "Capitals": -6,
        }
        const [id, tickets] = Object.entries(example)[0];
        const ticketData = tickets['tickets'];
        const requestWithUniqueTicketIDs = {}
        Object.keys(ticketData).map((ticketID, index) => {
            ticketData[ticketID].grouping = 'year';
            requestWithUniqueTicketIDs[index] = ticketData[ticketID];
        })
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
