from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import movie_detail, actor_detail, load_movies_from_db, load_actors_from_db

app = FastAPI(
    title="PetrFD",
    description="It is like csfd. Akorat ze vubec",
    version="0.0.1"
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
@app.get("/search")
def search(request: Request):
    return templates.TemplateResponse("search.html", {"request": request, "message": "Search"})


@app.get("/ping")
def ping():
    return "ok"


@app.get("/movie/{name}", response_class=HTMLResponse)
def movie_page(request: Request, name):
    actors = movie_detail(name)
    if actors:
        return templates.TemplateResponse("movie_page.html", {"request": request,
                                                              "movie_name": name,
                                                              "actors": actors})
    return templates.TemplateResponse("movie_not_found.html", {"request": request})


@app.get("/actor/{name}", response_class=HTMLResponse)
def movie_page(request: Request, name):
    movies = actor_detail(name)
    if movies:
        return templates.TemplateResponse("actor_page.html", {"request": request,
                                                              "actor_name": name,
                                                              "movies": movies})
    return templates.TemplateResponse("actor_not_found.html", {"request": request})


@app.get("/searchresultpage")
@app.post("/searchresultpage")
def search_result_page(request: Request, origin: str = Form("origin")):
    matched_movies = load_movies_from_db(origin)
    matched_actors = load_actors_from_db(origin)
    return templates.TemplateResponse("search_result_page.html", {"request": request,
                                                                  "text": origin,
                                                                  "actors": matched_actors,
                                                                  "movies": matched_movies})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8080, debug=True)
