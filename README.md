# The Gallica Grapher

### Pull requests and new contributors welcome! 

If you have an idea, suggestion, or question about the code, don't hesitate to make a pull request or new issue. 

This app relies heavily on the [Gallica API](https://api.bnf.fr/fr/api-document-de-gallica) and [Pyllicagram](https://github.com/regicid/pyllicagram). You can find the Gallica JSON API I built in the [gallica-getter](https://github.com/gleasonw/gallica-getter) repository.

## Important files:

#### [main.py](https://github.com/gleasonw/gallica-grapher/blob/main/backend/main.py)
* api routes for the frontend marked by the @app FastAPI decorator

#### [request.py](https://github.com/gleasonw/gallica-grapher/blob/main/backend/www/request.py)
* The Request class, a thread that spawns for each user and calls the core fetch --> parse --> store to database logic

[Component directory](https://github.com/gleasonw/gallica-grapher/tree/main/frontend/src/components)
* Contains the React components for the graph, table, paper dropdown, and every UI component. 
* The long className strings in the html elements are [Tailwind](https://tailwindcss.com/) CSS utility classes.
