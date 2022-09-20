import React from "react";
import styled from 'styled-components';
import ClassicUIBox from "./shared/ClassicUIBox";


const GallicaApiLink =
    <a
    href={'https://api.bnf.fr/fr/api-document-de-gallica'}
    target={'_blank'}
    rel={'noopener noreferrer'}
    >
        Gallica API
    </a>
//Wow, handcoding text in HTML is a pain. I expect future me is using a markdown parser.
export default function Info(props){
    return(
        <StyledInfoText>
            <ClassicUIBox>
                <h1>The Gallica Grapher</h1>
                <section>
                    <p>This tool exists thanks to the wondrously open and interesting {GallicaApiLink},
                    a product of the French National archives. I used the API for undergraduate research on
                    19th century French culture. Now that I have
                        graduated, time is momentarily (I hope) plentiful, and I'm trying my hand at making a website out of it.</p>
                </section>
                <h3>Do I need to speak French to use it?</h3>
                <section>
                    <p>Most of the periodicals in the archive are in French, so French words are most relevant. There are, though, a sizeable number of international or
                        European editions in English, such as the New York Herald. Play around with it!</p>
                </section>
                <section>
                    <p>Pour les francophones qui se demandent pourquoi ce site est en anglais : je vais traduire le site bientôt, je me concentre sur le système pour l'instant.</p>
                </section>
                <h3> How do I begin a search? </h3>
                <section>
                    <ol>
                        <li>Enter a term into the search bar;</li>
                        <br/>
                        <li>Select a grouping of periodicals to survey;</li>
                        <br/>
                        <li>If you would like to add a search (another trend line on the graph), click "compare";</li>
                        <br/>
                        <li>Click the 'Fetch and Graph 📊' button;</li>
                        <br/>
                        <li>Watch the results roll in. If your term is especially popular, I would recommend a cup of tea. Requests run concurrently, but to avoid
                            blasting the French national library's servers, I have erred on a smaller, more polite number of worker threads.</li>
                    </ol>
                </section>
                <h3>What do I see on the results page?</h3>
                <section>
                    <p>The Gallica API returns a record for any occurrence of a term in a periodical issue. I parse these records
                        and group occurrences within the same year, month, or on the same day to create a time series for each request.</p>
                </section>
                <section>
                    <p>

                    Beneath the chart is a table of the records pulled from Gallica, with links to the scanned periodical. Clicking on
                    a point in the chart will list the corresponding records. You can also make direct requests by entering
                    a date above the table. I'm still designing this section for better usability -- I think it's the most
                    interesting part of the tool. You can see cultural trends as they arise, then dive into the texts that
                    provide context.
                    </p>
                </section>
                <h3>Can I see the code?</h3>
                <section>
                    <p>
                        Yes! I would appreciate feedback or pull requests.
                    </p>
                    <p>
                        <a
                            href={'https://github.com/gleasonw/Gallica-ngram-grapher'}
                            target={'_blank'}
                            rel={'noopener noreferrer'}
                        >
                            Here's the repository.
                        </a>

                    </p>

                </section>
                <h3>A design citation</h3>
                <section>
                    Much of these pretty boxes and backgrounds exist thanks to inspect source and the good taste of the Lichess.com CSS designer. Merci.
                </section>

            </ClassicUIBox>
        </StyledInfoText>
    )
}

const StyledInfoText = styled.div`
    margin: 2vw auto 5vw auto;
    text-align: justify;
    border-collapse: separate;
    border-spacing: 0 5px;
    width: calc(100% - 40px);
    font-size: large;
    max-width: 900px;

`;
