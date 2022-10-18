# The Gallica Grapher

Culture and identity were once local, the products of word-of-mouth and conversation. The industrial press, developed throughout the early 19th century, brought daily or even twice-a-day updates to French citizens. Culture became national. Individual opinions ascended to group opinions; “public opinion” rose into being, looming over the political class, and the press was its handler.

This app integrates with a vast archive of periodicals through the Gallica API, allowing for rapid text searches over thousands of periodicals. The app routes requests to Gallica, parses the responses, and creates a trend line. Selecting a point will bring up the associated records in a table beneath the graph.


### Do I need to speak French to use it?

Most of the periodicals in the archive are in French, so French words are most relevant. There are, though, a sizeable number of international or 
European editions in English, such as the New York Herald. Play around with it!  

Pour les francophones qui se demandent pourquoi ce site est en anglais : je vais traduire le site bientôt, je me concentre sur le système pour l'instant.


### How do I begin a search?  

1. Enter a term into the search bar;  


2. Select a grouping of periodicals to survey;
3. If you would like to add a search (another trend line on the graph), click "compare";
3. Click the 'Fetch and Graph 📊' button;
4. Watch the results roll in. If your term is especially popular, I would recommend a cup of tea. Requests initSearch concurrently, but to avoid 
blasting the French national library's servers, I have erred on a smaller number of worker threads.

### What do I see on the results page?

The Gallica API returns a record for any occurrence of a term in a periodical issue. I parse these records
and group occurrences for a given bin size (year, month, or day) to create a time series for each request.  

Beneath the chart is a table of the records pulled from Gallica, with links to the scanned periodical. Clicking on
a point in the chart will list the corresponding records. You can also make direct requests by entering
a date above the table. I'm still designing this section for better usability -- I think it's the most
interesting part of the tool. You can see cultural trends as they arise, then dive into the texts that 
provide context.

### A design citation

Many of these pretty boxes and backgrounds exist thanks to inspect source and the good taste of the Lichess.com CSS designer. Merci.
