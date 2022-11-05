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
                    startMonth={props.startMonth}
                    startDay={props.startDay}
                    endYear={props.endYear}
                    endMonth={props.endMonth}
                    endDay={props.endDay}
                    onStartYearChange={props.onStartYearChange}
                    onStartMonthChange={props.onStartMonthChange}
                    onStartDayChange={props.onStartDayChange}
                    onEndYearChange={props.onEndYearChange}
                    onEndMonthChange={props.onEndMonthChange}
                    onEndDayChange={props.onEndDayChange}
                />
                {
                    props.selectedPaperBoundary &&
                    <div>(selected papers published between {props.selectedPaperBoundary[0]} and {props.selectedPaperBoundary[1]})</div>
                }

            </OptionWrap>
        </StyledOptionInput>
    )
}