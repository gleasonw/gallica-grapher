import React from "react";

export function Dropdown(props) {
    if (props.error) {
        return <div>Error: {props.error.message}</div>
    } else if (props.papers && props.papers.length > 0) {
        return (
            <ul className='paperDropdown'>
                {props.papers.map(paper => (
                    <DropdownItem
                        key={paper['code']}
                        paper={paper['title']}
                        onClick={() => props.onClick(paper)}
                    />
                ))}
            </ul>
        );
    } else {
        return null
    }
}

function DropdownItem(props) {
    return (
        <button
            type="button"
            className='paperDropdownItem'
            onClick={props.onClick}
        >
            {props.paper}
        </button>
    )
}