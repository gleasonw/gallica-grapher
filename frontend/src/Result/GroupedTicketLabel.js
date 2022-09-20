import React, {useContext} from 'react';
import {StyledTicketLabel} from "../shared/StyledTicketLabel";
import ItemsBlurb from "../shared/ItemsBlurb";
import {GraphSettingsContext} from "./GraphSettingsContext";
import ClassicUIBox from "../shared/ClassicUIBox";
import SeriesColorBubble from "../shared/SeriesColorBubble";

export default function GroupedTicketLabel(props){
    const settings = useContext(GraphSettingsContext);
    return(
        <div>
            {
                Object.keys(props.tickets).map((key, index) => {
                    const ticket = props.tickets[key];
                    const color = settings[key].color;
                    return (
                        <StyledTicketLabel key={key}>
                            Occurrences of <ItemsBlurb terms={ticket.terms}/>
                            in <ItemsBlurb papers={ticket["papersAndCodes"]}/>
                            from <ItemsBlurb dateRange={ticket["dateRange"]}/>
                            <SeriesColorBubble color={color}/>
                        </StyledTicketLabel>
                    )
                })
            }
        </div>
    )
}