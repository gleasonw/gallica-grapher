import React, {useEffect} from 'react';
import LesserButton from "../shared/LesserButton";

export default function OCRText(props) {
    const [arkCode, setArkCode] = React.useState('')
    const [loaded, setLoaded] = React.useState(false);
    const [ocrInfo, setOcrInfo] = React.useState('');
    const [buttonText, setButtonText] = React.useState('View context');

    useEffect(() => {
        if(props.arkCode !== arkCode) {
            setArkCode(props.arkCode);
            setLoaded(false);
            setOcrInfo('');
            setButtonText('View context');
        }
    }, [props.arkCode, arkCode]);

    async function handleClick() {
        setButtonText('Loading...');
        const ocrText = await fetch(`/api/ocrtext/${arkCode}/${props.term}`).then(
            response => response.json()
        )
        setOcrInfo(ocrText['text']);
        setLoaded(true);
    }

    if (loaded) {
        return ocrInfo.map((info) => {
            let pageNumberText = info[0];
            let pageNumber = pageNumberText.split('_').pop();
            let ocrText = info[1];
            let htmlPageLink =`https://gallica.bnf.fr/ark:/12148/${arkCode}.f${pageNumber}.item.texteBrut`
            return (
                <div key={pageNumberText}>
                    <a
                        href={htmlPageLink}
                        target='_blank'
                        rel='noopener noreferrer'
                    >
                        {pageNumberText}
                    </a>
                    <div dangerouslySetInnerHTML={{__html: ocrText}}/>
                </div>
                )
        })
    }else{
        return (
            <LesserButton onClick={handleClick}>
                {buttonText}
            </LesserButton>
        )
    }
}