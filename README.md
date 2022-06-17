# README #

### PetrFD is film database of top 1000 movies and its actors from http://www.csfd.cz

#### Search page ####

Welcome page with input field for search in movie and actors

When you click on "Search" button you will be redirected to Search result page

`http://localhost:8080/`

`http://localhost:8080/search`


#### Search result page ####
Page with search results for Actors and Movies. Contains also link to search homepage.

List of Actors and Movies and links to `/actor/{name}` and `/movie/{name}` endpoints

`http://localhost:8080/searchresultpage`

#### Actor Page ####
Page contains movies where actor star

`http://localhost:8080/actor/{name}`

e.g. `http://localhost:8080/actor/Tom%20Hanks`


#### Movie Page ####
Page contains list of all actors in the movie

`http://localhost:8080/movie/{name}`

e.g. `http://localhost:8080/movie/Forrest%20Gump`


## Architecture ##

App is build on `FASTAPI` framework with four endpoints described above. Scrapers of `http://csfd.cz` content are in `csfd_scraper.py` file. Packages used `aiohttp`, `requests`, `beautifulsoup`. Top 1000 movies is scraped asynchronously and then each movie is scraped in single thread to avoid blocking/DDoS attack. Possible TODO - rewrite it to scrapy or make request in batches via `aiohttp`. Results from scraping are stored in `actors.csv / movies.csv` files where from they are loaded to `sqlite3` database named `petrfd.db`. 

**DATA ARE ALREADY IN `petrfd.db` READY TO USE**

File `database.py` contains all methods for loading movies and actors to db as well as for searching in db according to input. Actors and Movies are not changing on CSFD often so I commented out running scraper and loading data to db. Uncomment if you want fresh data.  

#### Flaws of app ####
Data extraction can be done in better&faster (asynchronous) way - with scrapy as well as data processing does not require middle step via `.csv` files. But I focus more on design FastAPI app its endpoints and sqlite query. Nature of this data is that they cannot be refreshed often. 


### All is ready to use via Dockerfile
#### Commands for docker startup
App run on **port 8080**. Run commands, when current location is repository:
```
docker build -t petrfd:1.0 .
docker run -d -p 8080:8080 petrfd:1.0
```
