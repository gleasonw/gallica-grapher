# The Gallica Grapher

### Pull requests and new contributors welcome! 

If you have an idea, suggestion, or question about the code, don't hesitate to make a pull request or new issue. The core parsing code is written in Python, the frontend in Typescript and React. There are many items that could be improved. Readability, architecture, frontend design, something for everyone!

Here is a quick tour:

Important server-side files:

[main.py](https://github.com/gleasonw/gallica-grapher/blob/main/backend/main.py)
* api routes for the frontend marked by the @app FastAPI decorator
* The Request class, a thread that spawns for each user and calls the core fetch --> parse --> store to database logic

Important front end files:

[Component directory](https://github.com/gleasonw/gallica-grapher/tree/main/frontend/src/components)
* Contains the React code for the graph, table, paper dropdown, and every other UI component. 
* The long className strings in the html elements are [Tailwind](https://tailwindcss.com/) CSS utility classes.

[_app.ts](https://github.com/gleasonw/gallica-grapher/blob/main/frontend/src/server/routers/_app.ts)
* Components call a Next.js API through this router, which calls the Python API in main.py

Railway hosts the Python code, a Postgres database for storage and a Redis database for tracking user requests. Vercel hosts the Next.js frontend. It is all free! 







### Analyzing the Press

> "... a new way of linking fraternity, power and time meaningfully together ... [print-capitalism] made it possible for
> rapidly growing numbers of people to think about themselves, and to
> relate themselves to others, in profoundly new ways."
-- Benedict Anderson, *Imagined Communities*, [36](https://is.muni.cz/el/1423/jaro2016/SOC757/um/61816961/Benedict_Anderson_Imagined_Communities.pdf).

The 19th-century industrial press brought daily or even twice-a-day updates to French citizens. As wide distribution elevated individual opinions to group opinions, culture and identity became nationally cohesive. Public opinion -- "l'Opinion" -- rose into being, looming over the political class. The industrial press was its handler. Political scandal, colonial conquest, and national rivalry all passed through the printed word to determine, and shape, the people's will. 

This app integrates with the French National Archives [Gallica API](https://api.bnf.fr/fr/api-document-de-gallica) and [Gallicagram](https://shiny.ens-paris-saclay.fr/app/gallicagram) to explore trends across thousands of periodicals. Clicking on the graph pulls a sample of occurrences from that period.


### Do I need to speak French to use it?

Most of the periodicals in the archive are in French, so French words are most relevant. There are, though, a sizeable number of international or 
European editions in English, such as the New York Herald. Play around with it! 
