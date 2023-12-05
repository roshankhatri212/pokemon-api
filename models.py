# models.py
from pydantic import BaseModel
from typing import Optional

class PokemonBase(BaseModel):
    name: str
    image: str
    type: str

class Pokemon(PokemonBase):
    class Config:
        orm_mode = True

class PokemonFilter(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
