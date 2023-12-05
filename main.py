# main.py
from sqlalchemy.orm import Session
from fastapi import FastAPI, Query, Depends
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from typing import List
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models import Pokemon, PokemonBase, PokemonFilter
from database import get_db
from config import settings

app = FastAPI()

# Database setup
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create the table
class PokemonDB(Base):
    __tablename__ = "pokemon"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    image = Column(String)
    type = Column(String)

Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to filter Pokémon based on provided parameters
def filter_pokemons(db: Session, filters: PokemonFilter) -> List[Pokemon]:
    query = db.query(PokemonDB)

    if filters.name:
        query = query.filter(PokemonDB.name.ilike(f"%{filters.name}%"))
    if filters.type:
        query = query.filter(PokemonDB.type.ilike(f"%{filters.type}%"))

    pokemons = query.all()

    return pokemons

## Fetch Pokémon data from the PokeAPI and store it in the database
async def fetch_pokemon_data():
    async with AsyncClient() as client:
        response = await client.get("https://pokeapi.co/api/v2/pokemon?limit=100")
        data = response.json()["results"]

        db = SessionLocal()
        try:
            tasks = [save_pokemon_data(db, pokemon) for pokemon in data]
            await asyncio.gather(*tasks)
        finally:
            db.close()

async def save_pokemon_data(db, pokemon):
    db_pokemon = PokemonDB(name=pokemon["name"], image="", type="")
    db.add(db_pokemon)
    db.commit()

# Call the function to fetch Pokémon data
import asyncio
asyncio.run(fetch_pokemon_data())

# API endpoint to get the list of Pokémon with filtering
@app.get(f"/api/{settings.api_version}/pokemons/", response_model=List[Pokemon])
async def get_pokemons(
    db: Session = Depends(get_db),
    name: str = Query(None, title="Filter by name"),
    type: str = Query(None, title="Filter by type")
):
    filter_params = PokemonFilter(name=name, type=type)
    pokemons = filter_pokemons(db, filter_params)
    return pokemons
