import styled from 'styled-components';

const PrettyTextOverflow = styled.div`
    max-height: 100px;
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    &:hover {
        overflow: visible;
        text-overflow: visible;
    }
    `;

export default PrettyTextOverflow;