import {DateInputBox} from './DateInputBox';
import {StyledOptionInput} from './StyledOptionInput';
import OptionWrap from './OptionWrap';

export default function DateSelect(props){
    return(
        <StyledOptionInput
            selected
            borderRadius={'10px'}
        >
            <OptionWrap
                selected
                borderRadius={'10px'}
            >
                <DateInputBox
                    startDate={props.startDate}
                    endDate={props.endDate}
                    onstartDateChange={props.onstartDateChange}
                    onendDateChange={props.onendDateChange}
                />
            </OptionWrap>
        </StyledOptionInput>
    )
}