import styled from 'styled-components';

export function GallicaGramShoutOut(props){
    return(
        <StyledMessage>
            Data courtesy of the Gallicagram project. For more analyses and
            some R wizardry, please visit <a target='_blank' href="https://shiny.ens-paris-saclay.fr/app/gallicagram" rel="noreferrer">Gallicagram</a>.
        </StyledMessage>
    )
}

export function DataLimitationWarning(props){
    return(
        <StyledMessage>
            When searching specific periodicals, only one occurrence is counted per volume.
        </StyledMessage>
    )
}

export function DataOriginMismatch(props){
    return(
        <StyledMessage>
        </StyledMessage>
    )
}

const StyledMessage = styled.div`
    font-size: 1rem;
    margin: 1rem;
    border: 1px solid #d9d9d9; 
    padding: .5rem;
    `;