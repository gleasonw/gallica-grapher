# The Gallica Grapher

> "... the search was on, so to speak, for a new way of linking fraternity, power and time meaningfully together. Nothing perhaps more precipitated this search, nor
> made it more fruitful, than print-capitalism, which made it possible for
> rapidly growing numbers of people to think about themselves, and to
> relate themselves to others, in profoundly new ways."
-- Benedict Anderson, *Imagined Communities*, [36](https://is.muni.cz/el/1423/jaro2016/SOC757/um/61816961/Benedict_Anderson_Imagined_Communities.pdf).

The industrial press, developed throughout the early 19th century, brought daily or even twice-a-day updates to French citizens. Prior to mass media, culture and identity were local, the products of face-to-face community and conversation. Wide distribution elevated individual opinions to group opinions. Culture and identity became nationally cohesive; “public opinion” rose into being, looming over the political class, and the press was its handler.

This app integrates with the French National Archives [Gallica API](https://api.bnf.fr/fr/api-document-de-gallica) and [Gallicagram](https://shiny.ens-paris-saclay.fr/app/gallicagram) to allow rapid exploration of trends across thousands of periodicals. 


### Do I need to speak French to use it?

Most of the periodicals in the archive are in French, so French words are most relevant. There are, though, a sizeable number of international or 
European editions in English, such as the New York Herald. Play around with it!  


### How do I begin a search?  

1. Enter a term into the search bar;  


2. Select a grouping of periodicals to survey;
3. If you would like to add a search (another trend line on the graph), click "compare";
3. Click the 'Fetch and Graph 📊' button;
4. Watch the results roll in. If your term is especially popular, I would recommend a cup of tea. Requests run concurrently, but to avoid 
blasting the French national library's servers, I have erred on a smaller number of worker threads.

### What do I see on the results page?

Beneath the chart is a table of records pulled from Gallica, with links to the scanned periodical. Clicking on
a point in the chart will list the corresponding records. You can also make direct requests by entering
a date above the table. I'm still designing this section for better usability -- I think it's the most
interesting part of the tool. You can see cultural trends as they arise, then dive into the texts that 
provide context.

### A design citation

Many of these pretty boxes and backgrounds exist thanks to inspect source and the good taste of the Lichess.com CSS designer. Merci.
