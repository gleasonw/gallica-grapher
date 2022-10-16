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
                    startYear={props.startYear}
                    endYear={props.endYear}
                    onStartYearChange={props.onStartYearChange}
                    onEndYearChange={props.onEndYearChange}
                />
            </OptionWrap>
        </StyledOptionInput>
    )
}