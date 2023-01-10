import {StyledOptionInput} from './StyledOptionInput';
import OptionWrap from './OptionWrap';

export default function DateGroupSelect(props){
    return (
        <StyledOptionInput
            flexDirection={'row'}
            borderRadius={'10px'}
        >
            <OptionWrap
                selected = {props.selected === 0}
                children={'year'}
                onClick={() => props.onDateGroupClick(0)}
                borderRadius={'10px 0 0 10px'}
            />
            <OptionWrap
                children={'month'}
                selected = {props.selected === 1}
                onClick={() => props.onDateGroupClick(1)}
            />
            <OptionWrap
                selected = {props.selected === 2}
                children={'no grouping (fetch all volumes with >= 1 occurrence)'}
                onClick={() => props.onDateGroupClick(2)}
                borderRadius={'0 10px 10px 0'}
            />
        </StyledOptionInput>
    )
}