# The Gallica Grapher

### Pull requests and new contributors welcome! 

If you have an idea, suggestion, or question about the code, don't hesitate to make a pull request or new issue. 

#### Important server-side files:

[main.py](https://github.com/gleasonw/gallica-grapher/blob/main/backend/main.py)
* api routes for the frontend marked by the @app FastAPI decorator

[request.py](https://github.com/gleasonw/gallica-grapher/blob/main/backend/www/request.py)
* The Request class, a thread that spawns for each user and calls the core fetch --> parse --> store to database logic

Context is provided by the Gallica API. You can find the Python proxy API I built in the [gallica-getter](https://github.com/gleasonw/gallica-getter) repository.

#### Important client-side files:

[Component directory](https://github.com/gleasonw/gallica-grapher/tree/main/frontend/src/components)
* Contains the React components for the graph, table, paper dropdown, and every UI component. 
* The long className strings in the html elements are [Tailwind](https://tailwindcss.com/) CSS utility classes.
