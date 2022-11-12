import {StyledOptionInput} from './StyledOptionInput';
import OptionWrap from './OptionWrap';
import {DateSelect} from '../shared/DateSelect';
import LesserButton from '../shared/LesserButton';

export default function DateRangeSelect(props) {

    function handleApplyBoundary(){
        props.onStartYearChange(props.selectedPaperBoundary[0]);
        props.onEndYearChange(props.selectedPaperBoundary[1]);
    }

    return (
        <div>
            <StyledOptionInput
                selected
                borderRadius={'10px'}
            >
                <OptionWrap
                    selected
                    borderRadius={'10px'}
                    flexDirection={props.flexDirection}
                    justifyContent={props.justifyContent}
                    display={'flex'}
                >
                    <DateSelect
                        year={props.startYear}
                        month={props.startMonth}
                        day={props.startDay}
                        onYearChange={props.onStartYearChange}
                        onMonthChange={props.onStartMonthChange}
                        onDayChange={props.onStartDayChange}
                        flexDirection={props.flexDirection}
                    />
                    and
                    <DateSelect
                        year={props.endYear}
                        month={props.endMonth}
                        day={props.endDay}
                        onYearChange={props.onEndYearChange}
                        onMonthChange={props.onEndMonthChange}
                        onDayChange={props.onEndDayChange}
                        flexDirection={props.flexDirection}
                    />
                </OptionWrap>
            </StyledOptionInput>
            {
                props.selectedPaperBoundary &&
                <div>
                    (selected papers published
                    between {props.selectedPaperBoundary[0]} and {props.selectedPaperBoundary[1]})
                    <LesserButton onClick={handleApplyBoundary}>Apply</LesserButton>
                </div>
            }
        </div>
    )
}