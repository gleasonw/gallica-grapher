import React, {useState} from 'react';
import {v4 as uuidv4} from 'uuid';
import InputUI from "./InputUI";
import QueryProgressUI from "./QueryProgressUI";
import ResultUI from "./ResultUI";
import './style.css';
import 'bootstrap/dist/css/bootstrap.min.css';


function App() {
    const [tickets, setTickets] = useState([])
    const [gettingInput, setGettingInput] = useState(true)
    const [runningQueries, setRunningQueries] = useState(false)
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
        let updatedTickets = tickets.slice()
        for (let i = 0; i < tickets.length; i++){
            updatedTickets[i]['id'] = uuidv4();
        }
        setTickets(updatedTickets)
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
                    onTicketClick={handleTicketClick}
                />
            </div>
        )
    }else if(runningQueries){
          return (
            <div className="App">
                {header}
                <QueryProgressUI
                    tickets={tickets}
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