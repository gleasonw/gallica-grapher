import React from 'react';
import InputUI from "./InputUI";
import QueryProgressUI from "./QueryProgressUI";
import ResultUI from "./ResultUI";
import './style.css';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
    return (
        <div className="App">
            <header className="header">
                <div className="mainTitle">
                    <a className="homeLink">The Gallica Grapher</a>
                </div>
            </header>
            <InputUI/>
            <QueryProgressUI/>
            <ResultUI/>
        </div>
    );
}



export default App;