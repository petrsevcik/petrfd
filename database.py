import sqlite3
import csv


def clear_db(db_name, table_names):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    for table in table_names:
        cur.execute(f"""DELETE * FROM {table}""")
        con.commit()
    con.close()
    print(f"tables {table_names} removed from {db_name}")


def save_movie_to_db(db_name, movie):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movies 
        (`id` int, `name` varchar(255), `link` varchar(255), `year` int)
    """)
    cur.execute("""INSERT INTO movies
        ('id', 'name', 'link', 'year')
    VALUES
        (?, ?, ?, ?)""", movie)
    con.commit()
    con.close()


def save_actor_to_db(db_name, actor):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS actors 
        (`name` varchar(255), `actor_link` varchar(255), `movie_link` varchar(255))
    """)
    cur.execute("""INSERT INTO actors
        ('name', 'actor_link', 'movie_link')
    VALUES
        (?, ?, ?)""", actor)
    con.commit()
    con.close()


def movies_to_db(movies_csv_file):
    with open(movies_csv_file, 'r') as f:
        movies = csv.reader(f)
        for movie in movies:
            save_movie_to_db("petrfd.db", movie)
    print("Movies saved to db!")


def actors_to_db(actors_csv_file):
    with open(actors_csv_file, 'r') as f:
        actors = csv.reader(f)
        for actor in actors:
            save_actor_to_db("petrfd.db", actor)
    print("Actors saved to db!")


def load_movies_from_db(text):
    con = sqlite3.connect("petrfd.db")
    cur = con.cursor()
    wildcard = f'%{text}%'
    query = (cur.execute(f"""SELECT * FROM movies WHERE name LIKE \'{wildcard}\'"""))
    matched_movies = [movie for movie in query]
    return matched_movies


def load_actors_from_db(text):
    con = sqlite3.connect("petrfd.db")
    cur = con.cursor()
    wildcard = f'%{text}%'
    query = (cur.execute(f"""SELECT DISTINCT name, actor_link FROM actors WHERE name LIKE \'{wildcard}\'"""))
    matched_actors = [actor for actor in query]
    return matched_actors


def movie_detail(movie):
    con = sqlite3.connect("petrfd.db")
    cur = con.cursor()
    cur.execute(f"""SELECT link FROM movies WHERE name = '{movie}' COLLATE NOCASE""")
    movie_link = cur.fetchone()
    if not movie_link:
        return None
    query = cur.execute(f"""SELECT name, actor_link FROM actors WHERE movie_link='{movie_link[0]}'""")
    actors_in_movie = [actor for actor in query]
    return actors_in_movie


def actor_detail(actor):
    con = sqlite3.connect("petrfd.db")
    cur = con.cursor()
    query = cur.execute(f"""SELECT movies.name FROM actors 
                        JOIN movies ON actors.movie_link = movies.link 
                        WHERE actors.name = '{actor}' COLLATE NOCASE""")
    actors_in_movies = [actor[0] for actor in query]
    if not actors_in_movies:
        return None
    return actors_in_movies

# Data already in pertfd.db - Switch on only if you want to insert new scraped data
# if __name__ == "__main__":
#     clear_db("petrfd.db", ["movies", "actors"])
#     movies_to_db("movies.csv")
#     actors_to_db("actors.csv")
