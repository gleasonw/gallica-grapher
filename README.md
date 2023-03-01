# The Gallica Grapher

### Pull requests and new contributors welcome! 

If you have an idea, suggestion, or question about the code, don't hesitate to make a pull request or new issue. The core parsing code is written in Python, the frontend in Typescript and React. There are many items that could be improved. Readability, architecture, frontend design, something for everyone!

#### Important server-side files:

[main.py](https://github.com/gleasonw/gallica-grapher/blob/main/backend/main.py)
* api routes for the frontend marked by the @app FastAPI decorator
* Hosted at https://gallica-grapher-production.up.railway.app/ 

[request.py](https://github.com/gleasonw/gallica-grapher/blob/main/backend/www/request.py)
* The Request class, a thread that spawns for each user and calls the core fetch --> parse --> store to database logic

[gallicaGetter directory](https://github.com/gleasonw/gallica-grapher/tree/main/backend/gallicaGetter)
* contains gallicaWrapper.py, the base abstraction for fetching XML from Gallica and converting it to Python objects.
* each endpoint wrapper is kept in its own file (e.g. volumeOccurrenceWrapper.py)
* contains a [tests directory](https://github.com/gleasonw/gallica-grapher/tree/main/backend/gallicaGetter/tests) containing unit tests for important logic and each endpoint wrapper. Calls to Gallica are not mocked, so the entire suite takes ~10 seconds to run. 

#### Important client-side files:

[Component directory](https://github.com/gleasonw/gallica-grapher/tree/main/frontend/src/components)
* Contains the React code for the graph, table, paper dropdown, and every other UI component. 
* The long className strings in the html elements are [Tailwind](https://tailwindcss.com/) CSS utility classes.

Railway hosts the Python code, a Postgres database for storage and a Redis database for tracking request progress. Vercel hosts the Next.js frontend. It is all free! 
