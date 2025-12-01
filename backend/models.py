from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    total_points = Column(Integer, default=0)
    battles_won = Column(Integer, default=0)

    pokemon = relationship("Pokemon", back_populates="owner")

class Pokemon(Base):
    __tablename__ = "pokemon"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("players.id"))
    species_name = Column(String)
    level = Column(Integer)
    stats = Column(JSON)   # includes EV, IV, base stats
    moves = Column(JSON)   # 4 random moves
    sprite_url = Column(String)
    in_party = Column(Integer, default=0)  # 0 = PC, 1-6 = party slot

    owner = relationship("Player", back_populates="pokemon")
