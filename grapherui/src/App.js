import React, {useState, useCallback} from 'react';
import {v4 as uuidv4} from 'uuid';
import InputUI from "./InputUI";
import RunningQueriesUI from "./RunningQueriesUI";
import ResultUI from "./ResultUI";
import './style.css';
import 'bootstrap/dist/css/bootstrap.min.css';


function App() {
    const [tickets, setTickets] = useState([])
    const [idTickets, setIDTickets] = useState({})
    const [gettingInput, setGettingInput] = useState(false)
    const [runningQueries, setRunningQueries] = useState(false)
    let wrapperSetRunningQueries = useCallback(val => {
        setRunningQueries(val);
    }, [setRunningQueries]);
    const header =
        <header className="header">
            <div className="mainTitle">
                The Gallica Grapher
            </div>
        </header>
    function handleInputSubmit(event){
        event.preventDefault();
        generateTicketIDs();
        setGettingInput(false);
        setRunningQueries(true);
    }
    function handleCreateTicketClick(items){
        createTicketFromInput(items)
    }
    function handleTicketClick(index){
        deleteTicketAtIndex(index);
    }
    function generateTicketIDs(){
        let ticketsWithID = {};
        for (let i = 0; i < tickets.length; i++){
            let id = uuidv4()
            ticketsWithID[id] = tickets[i]
        }
        setIDTickets(ticketsWithID)
    }
    function createTicketFromInput(items){
        let updatedTickets = tickets.slice();
        updatedTickets.push(items);
        setTickets(updatedTickets)
    }
    function deleteTicketAtIndex(index){
        const updatedTickets = tickets.slice()
        updatedTickets.splice(index, 1)
        setTickets(updatedTickets)
    }
    if(gettingInput){
        return (
            <div className="App">
                {header}
                <InputUI
                    requestTickets={tickets}
                    onInputSubmit={handleInputSubmit}
                    onCreateTicketClick={handleCreateTicketClick}
                    onTicketClick={handleTicketClick}z
                />
            </div>
        )
    }else if(runningQueries){
          return (
            <div className="App">
                {header}
                <RunningQueriesUI
                    tickets={idTickets}
                    setRunningQueries={wrapperSetRunningQueries}
                />
            </div>
          )
    }else{
        return (
            <div className="App">
                {header}
                <ResultUI
                    tickets={tickets}
                />
            </div>
          )
    }
}



export default App;