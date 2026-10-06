from fastapi import FastAPI, HTTPException
from typing import List

from models import Movie, MovieCreate
from database import create_movie, read_movies, read_movie


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to the Movies CRUD API"}


@app.get("/movies", response_model=List[Movie])
def get_movies():
    return read_movies()


@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    movie = read_movie(movie_id)

    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie


@app.post("/movies")
def add_movie(movie: MovieCreate):
    movie_id = create_movie(movie)

    return {
        "id": movie_id,
        "message": "Movie created successfully"
    }
