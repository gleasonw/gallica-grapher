import React, {useState} from 'react';
import InputUI from "./InputUI";
import QueryProgressUI from "./QueryProgressUI";
import ResultUI from "./ResultUI";
import './style.css';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
    const [requestInfoGroups, setRequestInfoGroups] = useState([])
    const [gettingInput, setGettingInput] = useState(true)
    const [runningQueries, setRunningQueries] = useState(false)
    const header =
        <header className="header">
            <div className="mainTitle">
                The Gallica Grapher
            </div>
        </header>
    function initializeQueries(userTickets){
        setGettingInput(false)
        setRunningQueries(true)
        setRequestInfoGroups(userTickets)
    }
    if(gettingInput){
        return (
            <div className="App">
                {header}
                <InputUI
                    requestTickets={requestInfoGroups}
                    onSubmit={initializeQueries}
                />
            </div>
        )
    }else if(runningQueries){
          return (
            <div className="App">
                {header}
                <QueryProgressUI
                />
            </div>
          )
    }else{
        return (
            <div className="App">
                {header}
                <ResultUI/>
            </div>
          )
    }
}



export default App;