import styled from 'styled-components';

export function GallicaGramShoutOut(props){
    return(
        <StyledGallicaGramShoutOut>
            Data courtesy of the Gallicagram project. For more analyses and
            some R wizardry, please visit <a target='_blank' href="https://shiny.ens-paris-saclay.fr/app/gallicagram" rel="noreferrer">Gallicagram</a>.
        </StyledGallicaGramShoutOut>
    )
}

export function DataLimitationWarning(props){
    return(
        <StyledGallicaGramShoutOut>
            When searching specific periodicals, only one occurrence is counted per volume.
        </StyledGallicaGramShoutOut>
    )
}

const StyledGallicaGramShoutOut = styled.div`
    font-size: 1rem;
    margin: 1rem;
    border: 1px solid #d9d9d9; 
    padding: .5rem;
    `;