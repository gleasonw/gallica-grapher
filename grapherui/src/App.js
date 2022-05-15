import './App.css';
import React from 'react';

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <div className="mainTitle">
                    <a className="homeLink" href="http://127.0.0.1:5000/">The Gallica Grapher</a>
                </div>
            </header>
            <FormBox/>
        </div>
    );
}
class selectionBox extends React.Component{
    renderSelectionBubble(selectString){
        return(
            <selectionBubble
                selection={selectString}
                onClick={() => this.props.onClick(selectString)}
            />
        )
    }
}

function selectionBubble(props){
    //TODO: props.selection define upon creation?
    return (
        <div className='selectionBubble' id={props.selection}>
            <div className='delete'>X</div>
            <div className="selection">{props.selection}</div>
        </div>
    );
}

class FormBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            terms: null,
            splitTerms: null,
            papers: null,
            splitPapers: null,
            dateRange: null,
        };
    }

    render() {
        return (
            <form onSubmit ={this.handleSubmit}>
                <label>
                    Terms:
                    <input type="text" />
                    Papers:
                    <input type="text" />
                    Date range:
                    <input type="text" />
                </label>
            </form>
        )
    }

}



export default App;
