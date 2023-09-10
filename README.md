# The Gallica Grapher

### Pull requests and new contributors welcome! 

If you have an idea, suggestion, or question about the code, don't hesitate to make a pull request or new issue. 

This app relies on the [Gallica API](https://api.bnf.fr/fr/api-document-de-gallica) and [Pyllicagram](https://github.com/regicid/pyllicagram). You can find the Gallica JSON API I built in the [gallica-getter](https://github.com/gleasonw/gallica-getter) repository.

This project used to have an API until I started using [React server components](https://nextjs.org/docs/app/building-your-application/rendering/server-components). I now fetch gram data directly from Gallicagram, in the [relevant home component](https://github.com/gleasonw/gallica-grapher/tree/main/frontend/src/app/page.tsx). 

### Important files:

[Component directory](https://github.com/gleasonw/gallica-grapher/tree/main/frontend/src/app/components)
* Contains the React components for the graph, table, paper dropdown, and every UI component. 
* The long className strings in the html elements are [Tailwind](https://tailwindcss.com/) CSS utility classes.
