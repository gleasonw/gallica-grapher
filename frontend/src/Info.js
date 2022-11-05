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
                    <p>Culture and identity were once local, the products of word-of-mouth and idle conversation. 
                    The industrial press, developed throughout the early 19th century, brought daily or even twice-a-day updates to French citizens. 
                    Culture became national. Individual opinions ascended to group opinions; “public opinion” rose into being,
                    looming over the political class, and the press was its handler. </p>
                    <p>This app integrates with a vast archive of periodicals through the {GallicaApiLink}, allowing for rapid text searches over thousands of periodicals. The app routes requests to Gallica,
                        parses the responses, and creates a trend line.
                    Selecting a point will bring up the associated records in a table beneath the graph.
                    </p>
                </section>
                <h3>Do I need to speak French to use it?</h3>
                <section>
                    <p>Most of the periodicals in the archive are in French, so French words are most relevant. There are, though, a number of international editions in English. Play around with it!</p>
                </section>
                <section>
                    <p>Pour les francophones qui se demandent pourquoi ce site est en anglais : je vais traduire le site bientôt, je me concentre sur le système pour l'instant.</p>
                </section>
                <h3> How do I begin a search? </h3>
                <section>
                    <ol>
                        <li>Enter a term into the search bar;</li>
                        <li>For a finer search, link another term (e.g., "portland" within 5 words of "Oregon")</li>
                        <li>Select a grouping of periodicals to survey;</li>
                        <li>If you would like to add a second search, up to a maximum of 5, click "compare";</li>
                        <li>Click the 'Fetch and Graph 📊' button;</li>
                        <li>Watch the results roll in. If your term is popular, I would recommend a cup of tea. Requests run concurrently, but to avoid
                            blasting the French national library's servers, I have erred on a smaller number of worker threads.</li>
                    </ol>
                </section>
                <h3>What do I see on the results page?</h3>
                <section>
                    <p>The Gallica API returns a record for any occurrence of a term in a periodical issue. I parse these records
                        and group occurrences within the same year, month, or day to create a time series for each request.</p>
                </section>
                <section>
                    <p>
                    Beneath the chart is a table of the records pulled from Gallica, with links to text in which it occurs. Clicking on
                    a point in the chart will list the corresponding records. You can also make direct requests by entering
                    a date above the table.
                    </p>
                    <p>I'm still designing this section for better usability -- I think it's the most
                    interesting part of the tool. You can see cultural trends as they arise on the graph, then dive into the context.
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
