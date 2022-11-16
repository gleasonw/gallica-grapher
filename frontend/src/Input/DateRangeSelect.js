import {StyledOptionInput} from './StyledOptionInput';
import OptionWrap from './OptionWrap';
import {DateInputBox} from './DateInputBox';
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
                >
                    <DateInputBox
                        startYear={props.startYear}
                        endYear={props.endYear}
                        onStartYearChange={props.onStartYearChange}
                        onEndYearChange={props.onEndYearChange}
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