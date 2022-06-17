import asyncio
import aiohttp
from bs4 import BeautifulSoup
import requests
import csv

class CSFDScraper:
    CSFD_URL = "https://www.csfd.cz"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0"}

    async def get_data(self, session, url):
        async with session.get(url, headers=self.headers) as resp:
            page = await resp.text()
            return page

    def get_normal_data(self, url):
        r = requests.get(url, headers=self.headers)
        page = r.text
        return page, url

    async def top_movies_page_scraper(self, page):
        soup = BeautifulSoup(page, "html.parser")
        table_rows = soup.find_all("h3", class_="film-title-norating")
        movies = []
        for row in table_rows:
            movie_id = int(row.find("span", class_="film-title-user").text.strip().replace(".", ""))
            movie_title = row.find("a").get("title")
            movie_link = f'{self.CSFD_URL}{row.find("a").get("href")}'
            movie_year = int(row.find("span", class_="info").text.replace("(", "").replace(")", ""))
            movies.append([movie_id, movie_title, movie_link, movie_year])
        return movies

    async def movie_page_scraper(self, page):
        actors = []
        soup = BeautifulSoup(page, "html.parser")

        creators_info = soup.find("div", class_="creators")
        for category in creators_info.find_all("div"):
            if "hraj" in category.find("h4").text.lower():
                actors_array = category.find_all("a")
                for actor in actors_array:
                    if actor.text.strip() == "více":
                        continue
                    actor_name = actor.text.strip()
                    actor_link = f'{self.CSFD_URL}{actor.get("href")}'
                    actors.append([actor_name, actor_link])
        return actors

    def normal_movie_page_scraper(self, page, movie_link):
        actors = []
        soup = BeautifulSoup(page, "html.parser")

        creators_info = soup.find("div", class_="creators")
        for category in creators_info.find_all("div"):
            if "hraj" in category.find("h4").text.lower():
                actors_array = category.find_all("a")
                for actor in actors_array:
                    if actor.text.strip() == "více":
                        continue
                    actor_name = actor.text.strip()
                    actor_link = f'{self.CSFD_URL}{actor.get("href")}'
                    actors.append([actor_name, actor_link, movie_link])
        return actors

    def save_to_csv(self, data, filename):
        with open(filename, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
            print("Saved to csv!")


async def scrape_movies():
    session = aiohttp.ClientSession()
    csfd = CSFDScraper()
    movie_db = []

    async with session:
        tasks_movies = []
        for i in range(10):
            url = f"https://www.csfd.cz/zebricky/filmy/nejlepsi/?from={i}00"  # 000 working for top 1-99 movies
            tasks_movies.append(asyncio.ensure_future(csfd.get_data(session, url)))

        orig_data = await asyncio.gather(*tasks_movies)
        for data in orig_data:
            hundred_movies = await csfd.top_movies_page_scraper(data)
            movie_db.extend(hundred_movies)
    csfd.save_to_csv(movie_db, "movies.csv")
    return movie_db


# NOT USED - BEHAVE LIKE DDoS attack without splitting requests to batches
#TODO make it work // rewrite to scrapy
async def scrape_actors(movie_links):
    session = aiohttp.ClientSession(trust_env=True)
    csfd = CSFDScraper()
    raw_actors = []
    failed_movies = []

    async with session:
        tasks_actors = []
        for link in movie_links:
            tasks_actors.append(asyncio.ensure_future(csfd.get_data(session, link)))

        orig_data = await asyncio.gather(*tasks_actors)
        for i, data in enumerate(orig_data):
            try:
                actors = await csfd.movie_page_scraper(data)
                [x.append(movie_links[i]) for x in actors]
                print(f"{movie_links[i]} scraped!")
                raw_actors.extend(actors)
            except:
                print(f"Error with {movie_links[i]}, need to be checked")
                failed_movies.append(movie_links[i])
                continue
    csfd.save_to_csv(raw_actors, "actors.csv")
    print(f"Failed movies: {failed_movies}")
    return raw_actors


def csfd_scraper():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_movies())
    loop.close()
    with open("movies.csv", "r") as f:
        reader = csv.reader(f)
        movies = list(reader)
        movie_links = [x[2] for x in movies]
        for link in movie_links:
            csfd = CSFDScraper()
            page, link = csfd.get_normal_data(link)
            actors = csfd.normal_movie_page_scraper(page, link)
            csfd.save_to_csv(actors, "actors.csv")


# Data already in pertfd.db - Switch on only if you want to refresh data
#if __name__ == "__main__":
#    csfd_scraper()