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
            terms: [],
            splitTerms: null,
            papers: [],
            splitPapers: null,
            dateRange: null,
        };
        this.handleInputChange = this.handleInputChange.bind(this);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        this.setState({
            [name]: value
        });
    }
    handleSubmit(event) {
        //Ajax
    }
    removeBubble(yup){

    }
    render() {
        const terms = this.state.terms
        const papers = this.state.papers
        const termBubbles = terms.map(term =>
            {
                return (
                    <selectionBubble
                        selection={term}
                        onClick={() => this.removeBubble(term)}
                    />
                );
            }

        )
        const paperBubbles = papers.map(paper =>
            {
                return(
                    <selectionBubble
                        selection={paper}
                        onClick={() => this.removeBubble(paper)}
                    />
                );
            })
        return (
            <form onSubmit ={this.handleSubmit}>
                <label>
                    Terms:
                    <div className="inputContainer">
                        <ol>{termBubbles}</ol>
                        <input
                            name="terms"
                            type="text"
                            onChange={this.handleInputChange} />
                    </div>
                </label>
                <br />
                <label>
                    Papers:
                    <div className="inputContainer">
                        <ol>{paperBubbles}</ol>
                        <input
                            name="papers"
                            type="text"
                            onChange={this.handleInputChange} />
                    </div>
                </label>
                <br />
                <label>
                    Date range:
                    <input
                        name="dateRange"
                        type="text"
                        onChange={this.handleInputChange} />
                </label>

            </form>
        )
    }

}



export default App;